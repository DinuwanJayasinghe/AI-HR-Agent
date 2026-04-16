import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'screens/camera_screen.dart';

// Define cameras as a global variable so it’s accessible later
List<CameraDescription>? cameras;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Get available cameras before running the app
  try {
    cameras = await availableCameras();
  } catch (e) {
    debugPrint('Error getting cameras: $e');
    cameras = [];
  }

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Get the front camera (selfie camera)
    CameraDescription? frontCamera;
    String? errorMessage;

    if (cameras == null || cameras!.isEmpty) {
      errorMessage = 'No cameras found. Please allow camera access in your browser settings.';
    } else {
      try {
        frontCamera = cameras!.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.front,
        );
      } catch (e) {
        // If no front camera found, use the first available camera
        frontCamera = cameras!.first;
      }
    }

    // Open camera directly when app starts
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Face Recognition Attendance',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
      ),
      home: frontCamera != null
          ? CameraScreen(camera: frontCamera)
          : Scaffold(
              appBar: AppBar(
                title: const Text('Face Recognition Attendance'),
                backgroundColor: Colors.blue,
              ),
              body: Center(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.camera_alt_outlined,
                        size: 100,
                        color: Colors.grey,
                      ),
                      const SizedBox(height: 20),
                      Text(
                        errorMessage ?? 'No camera available',
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        'Instructions:\n'
                        '1. Allow camera permission when prompted\n'
                        '2. Refresh the page after granting permission',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 14, color: Colors.grey),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: () {
                          // Reload the page (for web)
                          // ignore: avoid_web_libraries_in_flutter
                          // This is a workaround - on web, user should manually refresh
                        },
                        child: const Text('Reload Page'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
    );
  }
}
