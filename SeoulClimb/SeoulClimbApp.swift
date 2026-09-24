import SwiftUI

@main
struct SeoulClimbApp: App {
    @State private var store = GymStore()
    @State private var location = LocationManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(store)
                .environment(location)
        }
    }
}
