//
//  AppDelegate.swift
//  ReplyCaddyTray
//
//  Created by Jed Tiotuico on 8/14/24.
//

import Cocoa
import SwiftUI

@main
class AppDelegate: NSObject, NSApplicationDelegate {

    @IBOutlet var window: NSWindow!
    var statusItem: NSStatusItem?

    @objc func runShellScript() {
        
    }

    @objc func saveFile() {
        print("Save File")
    }
    
    @objc func quitApp() {
        NSApplication.shared.terminate(self)
    }
    
    func applicationDidFinishLaunching(_ aNotification: Notification) {
        
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem?.button?.image = NSImage(named: "statusIcon")
        statusItem?.button?.target = self
        
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Run Shell Script", action: #selector(runShellScript), keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: "Save File", action: #selector(saveFile), keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(quitApp), keyEquivalent: ""))
        
        statusItem?.menu = menu
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }

    func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
        return true
    }


}

