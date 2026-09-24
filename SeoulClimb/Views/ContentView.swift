import SwiftUI

struct ContentView: View {
    @Environment(LocationManager.self) private var location

    var body: some View {
        TabView {
            GymMapView()
                .tabItem { Label("지도", systemImage: "map") }
            GymListView()
                .tabItem { Label("목록", systemImage: "list.bullet") }
        }
        .tint(.orange)
        .onAppear { location.start() }
    }
}
