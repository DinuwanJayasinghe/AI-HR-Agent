import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:path/path.dart' show join;
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';

class CameraScreen extends StatefulWidget {
  final CameraDescription camera;

  const CameraScreen({super.key, required this.camera});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  bool _hasCaptured = false; // prevent multiple captures
  bool _isProcessing = false;
  Position? _currentPosition;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(widget.camera, ResolutionPreset.high);
    _initializeControllerFuture = _controller.initialize().then((_) async {
      // Get location permission and current location
      await _getCurrentLocation();
      // Wait a brief moment for the camera to stabilize
      await Future.delayed(const Duration(seconds: 1));
      _autoCaptureImage();
    });
  }

  Future<void> _getCurrentLocation() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        debugPrint('Location services are disabled.');
        return;
      }

      // Check location permission
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          debugPrint('Location permissions are denied');
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        debugPrint('Location permissions are permanently denied');
        return;
      }

      // Get current position
      _currentPosition = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      debugPrint('Location: ${_currentPosition?.latitude}, ${_currentPosition?.longitude}');
    } catch (e) {
      debugPrint('Error getting location: $e');
    }
  }

  Future<void> _autoCaptureImage() async {
    if (_hasCaptured || _isProcessing) return;
    _hasCaptured = true;
    _isProcessing = true;

    try {
      // Show loading indicator
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (BuildContext context) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          },
        );
      }

      final XFile file = await _controller.takePicture();

      // For web, we work directly with XFile without saving to filesystem
      if (kIsWeb) {
        await _sendImageToBackendWeb(file);
      } else {
        // For mobile, save to temporary directory first
        final path = join(
          (await getTemporaryDirectory()).path,
          '${DateTime.now().millisecondsSinceEpoch}.png',
        );
        await file.saveTo(path);
        await _sendImageToBackend(path);
      }
    } catch (e) {
      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog
        _showErrorDialog('Error capturing image: $e');
      }
    } finally {
      _isProcessing = false;
    }
  }

  Future<void> _sendImageToBackendWeb(XFile imageFile) async {
    try {
      // For web, use localhost
      final url = Uri.parse('http://localhost:8000/attendance/recognize');

      var request = http.MultipartRequest('POST', url);

      // Read file as bytes and create multipart file from bytes
      final bytes = await imageFile.readAsBytes();
      request.files.add(http.MultipartFile.fromBytes(
        'image',
        bytes,
        filename: '${DateTime.now().millisecondsSinceEpoch}.png',
      ));

      // Add GPS coordinates to the request
      if (_currentPosition != null) {
        request.fields['latitude'] = _currentPosition!.latitude.toString();
        request.fields['longitude'] = _currentPosition!.longitude.toString();
      }

      var streamedResponse = await request.send().timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Connection timeout. Please check if the server is running.');
        },
      );

      var response = await http.Response.fromStream(streamedResponse);

      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog
      }

      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        _handleRecognitionResponse(data);
      } else {
        if (mounted) {
          _showErrorDialog('Server error: ${response.statusCode}');
        }
      }
    } catch (e) {
      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog if still open
        _showErrorDialog('Connection error: ${e.toString()}\n\nPlease ensure:\n1. Backend server is running\n2. Using correct URL (localhost:8000)\n3. No firewall blocking');
      }
    }
  }

  Future<void> _sendImageToBackend(String imagePath) async {
    try {
      // Change this URL to your backend IP address
      // For Android emulator: use 10.0.2.2
      // For physical device: use your computer's IP address (e.g., 192.168.1.100)
      final url = Uri.parse('http://10.0.2.2:8000/attendance/recognize');

      var request = http.MultipartRequest('POST', url);
      request.files.add(await http.MultipartFile.fromPath('image', imagePath));

      // Add GPS coordinates to the request
      if (_currentPosition != null) {
        request.fields['latitude'] = _currentPosition!.latitude.toString();
        request.fields['longitude'] = _currentPosition!.longitude.toString();
      }

      var streamedResponse = await request.send().timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          throw Exception('Connection timeout. Please check if the server is running.');
        },
      );

      var response = await http.Response.fromStream(streamedResponse);

      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog
      }

      if (response.statusCode == 200) {
        var data = json.decode(response.body);
        _handleRecognitionResponse(data);
      } else {
        if (mounted) {
          _showErrorDialog('Server error: ${response.statusCode}');
        }
      }
    } catch (e) {
      if (mounted) {
        Navigator.of(context).pop(); // Close loading dialog if still open
        _showErrorDialog('Connection error: ${e.toString()}\n\nPlease ensure:\n1. Backend server is running\n2. Using correct IP address\n3. No firewall blocking');
      }
    }
  }

  void _handleRecognitionResponse(Map<String, dynamic> data) {
    if (data.containsKey('error')) {
      String errorMessage = data['error'];
      if (errorMessage.contains('No face detected')) {
        _showRetryDialog('Face not clear, try again',
          'No face was detected in the image. Please try again with better lighting.');
      } else {
        _showRetryDialog('Error', errorMessage);
      }
      return;
    }

    List<dynamic> results = data['results'] ?? [];

    if (results.isEmpty) {
      _showRetryDialog('Face not clear, try again',
        'No face was detected. Please position your face clearly in front of the camera.');
      return;
    }

    var firstResult = results[0];

    if (firstResult['recognized'] == true) {
      // Face recognized successfully
      String employeeName = firstResult['employee_name'];
      String action = firstResult['action'];
      String department = firstResult['department'] ?? '';
      String position = firstResult['position'] ?? '';

      if (action == 'CHECK-IN') {
        _showWelcomeDialog(employeeName, department, position, firstResult);
      } else if (action == 'CHECK-OUT') {
        _showGoodbyeDialog(employeeName, department, position, firstResult);
      }
    } else {
      // Face not recognized
      _showRetryDialog('Face not clear, try again',
        'Face not recognized. Please ensure you are registered in the system or try again.');
    }
  }

  void _showWelcomeDialog(String name, String department, String position, Map<String, dynamic> data) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.green, size: 30),
              const SizedBox(width: 10),
              const Text('Welcome!'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Hello, $name!',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Text('Department: $department'),
              Text('Position: $position'),
              const SizedBox(height: 10),
              Text(
                'Check-in time: ${_formatTime(data['check_in'])}',
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green),
              ),
              const SizedBox(height: 10),
              const Text('Have a great day at work!'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _resetCapture();
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  void _showGoodbyeDialog(String name, String department, String position, Map<String, dynamic> data) {
    double workHours = data['work_hours'] ?? 0.0;
    double overtimeHours = data['overtime_hours'] ?? 0.0;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Row(
            children: [
              const Icon(Icons.waving_hand, color: Colors.orange, size: 30),
              const SizedBox(width: 10),
              const Text('Goodbye!'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'See you later, $name!',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              Text('Department: $department'),
              Text('Position: $position'),
              const SizedBox(height: 10),
              Text(
                'Check-out time: ${_formatTime(data['check_out'])}',
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.orange),
              ),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Work Hours: ${workHours.toStringAsFixed(2)} hrs',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    if (overtimeHours > 0)
                      Text(
                        'Overtime: ${overtimeHours.toStringAsFixed(2)} hrs',
                        style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
                      ),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              const Text('Thank you for your hard work today!'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _resetCapture();
              },
              child: const Text('OK'),
            ),
          ],
        );
      },
    );
  }

  void _showRetryDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Row(
            children: [
              const Icon(Icons.error_outline, color: Colors.red, size: 30),
              const SizedBox(width: 10),
              Text(title),
            ],
          ),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _resetCapture();
              },
              child: const Text('Try Again'),
            ),
          ],
        );
      },
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.error, color: Colors.red, size: 30),
              SizedBox(width: 10),
              Text('Error'),
            ],
          ),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _resetCapture();
              },
              child: const Text('Try Again'),
            ),
          ],
        );
      },
    );
  }

  void _resetCapture() {
    setState(() {
      _hasCaptured = false;
      _isProcessing = false;
    });
    // Get fresh location and trigger auto-capture again after a brief delay
    Future.delayed(const Duration(seconds: 1), () async {
      if (mounted) {
        await _getCurrentLocation();
        _autoCaptureImage();
      }
    });
  }

  String _formatTime(String? timestamp) {
    if (timestamp == null) return 'N/A';
    try {
      DateTime dt = DateTime.parse(timestamp);
      return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}:${dt.second.toString().padLeft(2, '0')}';
    } catch (e) {
      return timestamp;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Face Recognition Attendance'),
        backgroundColor: Colors.blue,
      ),
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Stack(
              children: [
                CameraPreview(_controller),
                Positioned(
                  bottom: 20,
                  left: 20,
                  right: 20,
                  child: Container(
                    padding: const EdgeInsets.all(15),
                    decoration: BoxDecoration(
                      color: Colors.black54,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      'Position your face in front of the camera',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.white, fontSize: 16),
                    ),
                  ),
                ),
              ],
            );
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }
}
