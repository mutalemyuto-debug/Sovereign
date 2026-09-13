# Sovereign Android APK

This is a WebView wrapper for the deployed Sovereign Django app.

- App name: Sovereign
- Package name: com.sovereign.app
- Website: https://sovereign-7str.onrender.com

## Build with Android Studio

1. Install Android Studio and the Android SDK.
2. Open this `android` folder in Android Studio.
3. Allow Gradle sync to finish.
4. Select `Build > Build Bundle(s) / APK(s) > Build APK(s)`.
5. Find the APK under `app/build/outputs/apk/debug/app-debug.apk`.

The APK needs an internet connection because the Django backend and database remain on Render.
