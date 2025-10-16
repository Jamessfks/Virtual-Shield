#!/usr/bin/env python3
"""
AI Screenshot Detector - Professional Edition
A robust macOS application for AI detection in screenshots using Reality Defender.
"""

from realitydefender import RealityDefender
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import datetime
import os
import threading
import json
import subprocess
import tempfile
import sys
from typing import Optional, Tuple, Dict, Any, List
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MacOSScreenCapture:
    """Professional macOS screen capture utility using native screencapture command"""
    
    @staticmethod
    def capture_fullscreen() -> Optional[str]:
        """
        Capture fullscreen using macOS native screencapture
        
        Returns:
            Optional[str]: Path to captured image file, None if failed
        """
        try:
            # Create temporary file
            temp_file = tempfile.mktemp(suffix='.png')
            
            # Use macOS screencapture command for fullscreen
            # -x: Don't play sound
            # -t png: Save as PNG format
            result = subprocess.run([
                'screencapture', 
                '-x',
                '-t', 'png',
                temp_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                logger.info("Fullscreen capture successful")
                return temp_file
            else:
                logger.error(f"screencapture failed: {result.stderr}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("screencapture timed out")
            return None
        except Exception as e:
            logger.error(f"Error in fullscreen capture: {e}")
            return None
    
    @staticmethod
    def capture_area_interactive() -> Optional[str]:
        """
        Capture area using macOS native screencapture with interactive selection
        
        Returns:
            Optional[str]: Path to captured image file, None if failed or canceled
        """
        try:
            # Create temporary file
            temp_file = tempfile.mktemp(suffix='.png')
            
            # Use macOS screencapture command for interactive area selection
            # -i: Interactive selection (like Cmd+Shift+4)
            # -x: Don't play sound
            # -t png: Save as PNG format
            result = subprocess.run([
                'screencapture', 
                '-i',
                '-x',
                '-t', 'png',
                temp_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                logger.info("Area capture successful")
                return temp_file
            else:
                logger.info("Area selection canceled or failed")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Area selection timed out")
            return None
        except Exception as e:
            logger.error(f"Error in area capture: {e}")
            return None

class ScreenshotAnalyzer:
    """Professional AI Screenshot Detector with Reality Defender integration"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Screenshot Detector Pro")
        self.root.geometry("950x750")
        self.root.minsize(800, 600)
        
        # Configure window properties
        self.root.configure(bg='#f8f9fa')
        
        # Configure style
        self._setup_styles()
        
        # Create screenshots folder
        self.screenshots_folder = Path("screenshots")
        self._ensure_screenshots_folder()
        
        # Initialize Reality Defender client
        self.rd_client: Optional[RealityDefender] = None
        self._initialize_reality_defender()
        
        # Results storage
        self.analysis_results: List[Dict[str, Any]] = []
        
        # Screenshot mode
        self.screenshot_mode = tk.StringVar(value="fullscreen")
        
        # UI state
        self.is_processing = False
        
        # Setup GUI and error handling
        self._setup_gui()
        self._setup_error_handling()
    
    def _setup_styles(self) -> None:
        """Configure ttk styles for professional appearance"""
        style = ttk.Style()
        style.theme_use('aqua')  # Use native macOS theme
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('SF Pro Display', 20, 'bold'))
        style.configure('Subtitle.TLabel', font=('SF Pro Text', 12), foreground='#6c757d')
        style.configure('Status.TLabel', font=('SF Pro Text', 10))
        style.configure('Accent.TButton', font=('SF Pro Text', 12, 'bold'))
    
    def _ensure_screenshots_folder(self) -> None:
        """Ensure screenshots folder exists"""
        try:
            self.screenshots_folder.mkdir(exist_ok=True)
            logger.info(f"Screenshots folder ready: {self.screenshots_folder.absolute()}")
        except Exception as e:
            logger.error(f"Failed to create screenshots folder: {e}")
            messagebox.showerror("Error", f"Could not create screenshots folder: {e}")
            sys.exit(1)
    
    def _initialize_reality_defender(self) -> None:
        """Initialize Reality Defender client with error handling"""
        try:
            api_key = "rd_d3d3eac041426e52_1cb3a26dc710d98f1603883f38e51753"
            self.rd_client = RealityDefender(api_key=api_key)
            logger.info("Reality Defender client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Reality Defender: {e}")
            self.rd_client = None
            messagebox.showwarning(
                "Reality Defender Warning", 
                "Could not initialize Reality Defender.\nScreenshots will be saved but not analyzed.\n\n"
                "Please check your internet connection and API key."
            )
    
    def _setup_error_handling(self) -> None:
        """Setup global error handling for the application"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}\n\n"
                "The application will continue running."
            )
        
        sys.excepthook = handle_exception
    
    def _setup_gui(self) -> None:
        """Setup the main GUI components"""
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="25")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(4, weight=1)
        
        # Create GUI sections
        self._create_header(main_container)
        self._create_mode_selection(main_container)
        self._create_action_section(main_container)
        self._create_progress_section(main_container)
        self._create_results_section(main_container)
        self._create_control_buttons(main_container)
    
    def _create_header(self, parent: ttk.Frame) -> None:
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        
        title_label = ttk.Label(
            header_frame, 
            text="🤖 AI Screenshot Detector", 
            style='Title.TLabel'
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Professional AI detection powered by Reality Defender",
            style='Subtitle.TLabel'
        )
        subtitle_label.pack(pady=(8, 0))
    
    def _create_mode_selection(self, parent: ttk.Frame) -> None:
        """Create screenshot mode selection"""
        mode_frame = ttk.LabelFrame(parent, text=" Screenshot Mode ", padding="20")
        mode_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Full screen option
        fullscreen_frame = ttk.Frame(mode_frame)
        fullscreen_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Radiobutton(
            fullscreen_frame, 
            text="🖥️  Full Screen Capture", 
            variable=self.screenshot_mode, 
            value="fullscreen"
        ).pack(anchor="w")
        
        ttk.Label(
            fullscreen_frame,
            text="    Captures the entire screen",
            style='Subtitle.TLabel'
        ).pack(anchor="w")
        
        # Area selection option
        area_frame = ttk.Frame(mode_frame)
        area_frame.pack(fill="x")
        
        ttk.Radiobutton(
            area_frame, 
            text="🎯  Interactive Area Selection", 
            variable=self.screenshot_mode, 
            value="area"
        ).pack(anchor="w")
        
        ttk.Label(
            area_frame,
            text="    Click and drag to select area (like ⌘⇧4)",
            style='Subtitle.TLabel'
        ).pack(anchor="w")
    
    def _create_action_section(self, parent: ttk.Frame) -> None:
        """Create main action button"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        self.action_button = ttk.Button(
            action_frame,
            text="📸  Capture & Analyze Screenshot",
            command=self._on_capture_clicked,
            style="Accent.TButton"
        )
        self.action_button.pack(fill="x", ipady=8)
    
    def _create_progress_section(self, parent: ttk.Frame) -> None:
        """Create progress bar and status label"""
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            mode='indeterminate'
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready to capture screenshot",
            style='Status.TLabel'
        )
        self.status_label.grid(row=1, column=0)
    
    def _create_results_section(self, parent: ttk.Frame) -> None:
        """Create results table section"""
        results_frame = ttk.LabelFrame(parent, text=" Analysis Results ", padding="15")
        results_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(results_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ("Timestamp", "Filename", "Type", "Status", "AI Score", "Confidence")
        self.results_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings", 
            height=10
        )
        
        # Configure columns
        column_configs = {
            "Timestamp": {"width": 140, "anchor": "center"},
            "Filename": {"width": 220, "anchor": "w"},
            "Type": {"width": 100, "anchor": "center"},
            "Status": {"width": 130, "anchor": "center"},
            "AI Score": {"width": 80, "anchor": "center"},
            "Confidence": {"width": 90, "anchor": "center"}
        }
        
        for col, config in column_configs.items():
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, **config)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    def _create_control_buttons(self, parent: ttk.Frame) -> None:
        """Create control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, pady=15)
        
        buttons = [
            ("📁  Open Folder", self._open_screenshots_folder),
            ("💾  Export Results", self._export_results),
            ("🗑️  Clear Results", self._clear_results)
        ]
        
        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command).pack(
                side="left", padx=8
            )
    
    def _on_capture_clicked(self) -> None:
        """Handle capture button click"""
        if self.is_processing:
            return
        
        # Start capture process in separate thread
        capture_thread = threading.Thread(target=self._capture_and_analyze, daemon=True)
        capture_thread.start()
    
    def _schedule_ui_update(self, method, *args) -> None:
        """Safely schedule UI updates from background threads"""
        self.root.after(0, lambda: method(*args))
    
    def _capture_and_analyze(self) -> None:
        """Capture screenshot and analyze with Reality Defender"""
        try:
            self._set_processing_state(True)
            
            mode = self.screenshot_mode.get()
            self._update_status(f"Preparing {mode} capture...")
            
            # Capture screenshot based on mode
            temp_image_path = None
            if mode == "fullscreen":
                temp_image_path = MacOSScreenCapture.capture_fullscreen()
                capture_type = "fullscreen"
            else:  # area
                self._update_status("Select area on screen...")
                temp_image_path = MacOSScreenCapture.capture_area_interactive()
                capture_type = "area"
            
            if temp_image_path is None:
                self._update_status("Capture canceled or failed")
                return
            
            # Save screenshot to permanent location
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"screenshot_{capture_type}_{timestamp}.png"
            final_path = self.screenshots_folder / filename
            
            # Move temp file to final location
            os.rename(temp_image_path, str(final_path))
            
            self._update_status("Screenshot saved. Analyzing with Reality Defender...")
            
            # Analyze with Reality Defender if available
            if self.rd_client:
                try:
                    result = self.rd_client.detect_file(str(final_path))
                    status = result.get('status', 'UNKNOWN')
                    score = result.get('score', 0.0)
                    if score is None:
                        score = 0.0
                    confidence = self._get_confidence_level(score)
                    
                    # Store result
                    result_data = {
                        'timestamp': timestamp,
                        'filename': filename,
                        'filepath': str(final_path),
                        'capture_type': capture_type,
                        'status': status,
                        'score': score,
                        'confidence': confidence,
                        'full_result': result
                    }
                    
                    self.analysis_results.append(result_data)
                    
                    # Update GUI in main thread
                    self._schedule_ui_update(self._add_result_to_table, result_data)
                    status_msg = f"Analysis complete: {status} (Score: {score:.3f})"
                    self._schedule_ui_update(self._update_status, status_msg)
                    
                except Exception as analysis_error:
                    logger.error(f"Reality Defender analysis failed: {analysis_error}")
                    error_msg = f"Screenshot saved but analysis failed: {analysis_error}"
                    self._schedule_ui_update(self._update_status, error_msg)
            else:
                status_msg = "Screenshot saved (Reality Defender not available)"
                self._schedule_ui_update(self._update_status, status_msg)
                
        except Exception as capture_error:
            logger.error(f"Error in capture and analyze: {capture_error}")
            error_msg = f"Error: {capture_error}"
            self._schedule_ui_update(self._update_status, error_msg)
            self._schedule_ui_update(messagebox.showerror, "Error", str(capture_error))
        finally:
            self._schedule_ui_update(self._set_processing_state, False)
    
    def _set_processing_state(self, processing: bool) -> None:
        """Set the processing state and update UI"""
        self.is_processing = processing
        
        if processing:
            self.action_button.config(state="disabled", text="🔄  Processing...")
            self.progress_bar.start()
        else:
            self.action_button.config(state="normal", text="📸  Capture & Analyze Screenshot")
            self.progress_bar.stop()
    
    def _update_status(self, message: str) -> None:
        """Update status label"""
        self.status_label.config(text=message)
        logger.info(f"Status: {message}")
    
    def _get_confidence_level(self, score: float) -> str:
        """Convert score to confidence level"""
        if score >= 0.8:
            return "High"
        elif score >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def _add_result_to_table(self, result_data: Dict[str, Any]) -> None:
        """Add analysis result to the table"""
        values = (
            result_data['timestamp'],
            result_data['filename'],
            result_data['capture_type'].upper(),
            result_data['status'],
            f"{result_data['score']:.3f}",
            result_data['confidence']
        )
        
        item = self.results_tree.insert("", 0, values=values)  # Insert at top
        
        # Color coding based on status
        if result_data['status'] == 'MANIPULATED':
            self.results_tree.set(item, "Status", "🚨 AI DETECTED")
        elif result_data['status'] == 'AUTHENTIC':
            self.results_tree.set(item, "Status", "✅ AUTHENTIC")
        
        # Scroll to the new item
        self.results_tree.see(item)
        self.results_tree.selection_set(item)
    
    def _open_screenshots_folder(self) -> None:
        """Open the screenshots folder in Finder"""
        try:
            subprocess.run(['open', str(self.screenshots_folder)], check=True)
        except Exception as e:
            logger.error(f"Could not open screenshots folder: {e}")
            messagebox.showerror("Error", f"Could not open folder: {e}")
    
    def _export_results(self) -> None:
        """Export results to JSON file"""
        if not self.analysis_results:
            messagebox.showwarning("No Data", "No results to export")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Analysis Results"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str, ensure_ascii=False)
                
                messagebox.showinfo("Export Successful", f"Results exported to:\n{filename}")
                logger.info(f"Results exported to {filename}")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Could not export results:\n{e}")
    
    def _clear_results(self) -> None:
        """Clear all results"""
        if not self.analysis_results:
            messagebox.showinfo("No Data", "No results to clear")
            return
            
        if messagebox.askyesno("Confirm Clear", 
                              "Are you sure you want to clear all analysis results?\n\n"
                              "This action cannot be undone."):
            self.analysis_results.clear()
            
            # Clear table
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            self._update_status("Results cleared")
            logger.info("Analysis results cleared")
    
    def run(self) -> None:
        """Start the GUI application"""
        try:
            logger.info("Starting AI Screenshot Detector")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", str(e))
        finally:
            logger.info("Application closed")

def main():
    """Main application entry point"""
    try:
        app = ScreenshotAnalyzer()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
