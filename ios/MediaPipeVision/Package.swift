// swift-tools-version: 5.8

import PackageDescription

// Binary URLs and checksums come from Google's MediaPipe v1.2.3 Package.swift.
let package = Package(
    name: "MediaPipeVision",
    platforms: [.iOS(.v15)],
    products: [
        .library(
            name: "MediaPipeTasksVision",
            targets: ["MediaPipeTasksVision", "MediaPipeVisionLinkage"]
        ),
    ],
    targets: [
        .binaryTarget(
            name: "MediaPipeTasksCommonBinary",
            url: "https://dl.google.com/cpdc/20261111-125016/MediaPipeTasksCommon-1.2.3.xcframework.zip",
            checksum: "39990d7ff26dedeef5e0f43e7a8656ead9219b52133ae390af5e9ffcfa208b1f"
        ),
        .binaryTarget(
            name: "MediaPipeTaskGraphsBinary",
            url: "https://dl.google.com/cpdc/20261111-125016/MediaPipeTaskGraphs-1.2.3.xcframework.zip",
            checksum: "706d2c894767e281ac5c02c27f1f4bba3c1f88b25a1a0ef51d134685ae30e05c"
        ),
        .binaryTarget(
            name: "MediaPipeTasksVision",
            url: "https://dl.google.com/cpdc/20261111-125016/MediaPipeTasksVision-1.2.3.xcframework.zip",
            checksum: "5b420e4ce53681dbccc1b7ddcda3bd90a84d3e8c5f5b465abf02968d5155ceb1"
        ),
        .target(
            name: "MediaPipeVisionLinkage",
            dependencies: ["MediaPipeTasksCommonBinary", "MediaPipeTaskGraphsBinary", "MediaPipeTasksVision"],
            resources: [.copy("PrivacyInfo.xcprivacy")],
            linkerSettings: [
                // Keep the static initializers that register MediaPipe's graph calculators.
                .unsafeFlags(["-Xlinker", "-all_load"]),
                .linkedLibrary("c++"),
                .linkedLibrary("sqlite3"),
                .linkedFramework("Accelerate"),
                .linkedFramework("AVFoundation"),
                .linkedFramework("CoreMedia"),
                .linkedFramework("AudioToolbox"),
                .linkedFramework("CoreGraphics"),
                .linkedFramework("CoreImage"),
                .linkedFramework("CoreVideo"),
                .linkedFramework("QuartzCore"),
            ]
        ),
    ]
)
