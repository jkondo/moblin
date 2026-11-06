from pathlib import Path
import shutil

root = Path.cwd()
out = root / 'BrowserValidation'
source = out / 'Sources'
tests = out / 'Tests'
source.mkdir(parents=True, exist_ok=True)
tests.mkdir(exist_ok=True)
settings = (root / 'Moblin/Various/Settings/Settings.swift').read_text()
settings = settings[settings.index('class WebBrowserBookmarkSettings:'):settings.index('class SettingsAlertsMediaGalleryItem:')]
helpers = (root / 'Common/Various/CommonUtils.swift').read_text()
helpers = helpers[helpers.index('extension KeyedEncodingContainer {'):]
(source / 'Settings.swift').write_text('import SwiftUI\n' + settings + helpers)
view = (root / 'Moblin/View/WebBrowser/WebBrowserView.swift').read_text()
webview = view[view.index('struct WebView:'):view.index('private struct UrlView:')]
smallview = view[view.index('private struct WebBrowserSmallView:'):view.index('private struct WebBrowserBigView:')]
support = '''
let segmentHeight = 40.0
let segmentHeightBig = 50.0
class Database: ObservableObject { @Published var bigButtons = false }
@MainActor class WebBrowserState: ObservableObject { @Published var isSmall = true }
@MainActor class Model: ObservableObject {
    let browser = WKWebView()
    let database = Database()
    let settings = WebBrowserSettings()
    let state = WebBrowserState()
    func getWebBrowser() -> WKWebView { browser }
    func storeSettings() {}
    func makeToast(title: String) {}
}
@main struct BrowserValidationApp: App {
    @StateObject var model = Model()
    var body: some Scene {
        WindowGroup {
            WebBrowserSmallView(model: model, database: model.database,
                                webBrowser: model.settings, webBrowserState: model.state)
        }
    }
}
'''
(source / 'View.swift').write_text('import SwiftUI\nimport WebKit\n' + webview + smallview + support)
shutil.copy2(root / 'Moblin/Various/WebBrowserWindowLayout.swift', source)
shutil.copy2(root / 'MoblinTests/Moblin/Various/WebBrowserWindowLayoutSuite.swift', tests)
(out / 'project.yml').write_text('''
name: BrowserValidation
options:
  deploymentTarget:
    iOS: '18.5'
settings:
  base:
    SWIFT_VERSION: '6.0'
    SUPPORTS_MACCATALYST: YES
    GENERATE_INFOPLIST_FILE: YES
    CODE_SIGN_STYLE: Manual
    CODE_SIGN_IDENTITY: '-'
    CODE_SIGNING_REQUIRED: NO
targets:
  Moblin:
    type: application
    platform: iOS
    sources: [Sources]
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: org.jkondo.BrowserValidation
  MoblinTests:
    type: bundle.unit-test
    platform: iOS
    sources: [Tests]
    dependencies:
      - target: Moblin
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: org.jkondo.BrowserValidation.Tests
schemes:
  BrowserValidation:
    build:
      targets:
        Moblin: all
    test:
      targets: [MoblinTests]
''')
