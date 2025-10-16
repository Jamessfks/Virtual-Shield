from realitydefender import RealityDefender
import pyautogui
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import datetime
import os
import threading
from PIL import Image, ImageTk, ImageDraw
import json
import pyscreenshot as ImageGrab

class AreaSelector:
    def __init__(self, screenshot):
        self.screenshot = screenshot
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None
        self.selected_area = None
        
        # Create fullscreen window for area selection
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='black')
        self.root.attributes('-topmost', True)
        
        # Create canvas
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Escape>', self.cancel_selection)
        self.root.bind('<Escape>', self.cancel_selection)
        
        # Instructions
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            50,
            text="Click and drag to select area, press ESC to cancel",
            fill='white',
            font=('Arial', 16)
        )
        
        self.canvas.focus_set()
    
    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
    
    def on_drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2
            )
    
    def on_release(self, event):
        if self.start_x is not None and self.start_y is not None:
            self.end_x = event.x
            self.end_y = event.y
            
            # Calculate selected area
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:  # Minimum selection size
                self.selected_area = (x1, y1, x2, y2)
                self.root.destroy()
            else:
                messagebox.showwarning("Selection Too Small", "Please select a larger area")
    
    def cancel_selection(self, event=None):
        self.selected_area = None
        self.root.destroy()
    
    def get_selection(self):
        self.root.wait_window()
        return self.selected_area

class ScreenshotAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Screenshot Detector - Reality Defender")
        self.root.geometry("850x650")
        
        # Create screenshots folder
        self.screenshots_folder = "screenshots"
        if not os.path.exists(self.screenshots_folder):
            os.makedirs(self.screenshots_folder)
        
        # Reality Defender client
        self.rd_client = RealityDefender(api_key="rd_d3d3eac041426e52_1cb3a26dc710d98f1603883f38e51753")
        
        # Results storage
        self.analysis_results = []
        
        # Screenshot mode
        self.screenshot_mode = tk.StringVar(value="fullscreen")
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title_label = ttk.Label(main_frame, text="AI Screenshot Detector", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Screenshot mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Screenshot Mode", padding="10")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="📺 Full Screen", 
                       variable=self.screenshot_mode, value="fullscreen").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="🔲 Select Area", 
                       variable=self.screenshot_mode, value="area").pack(side=tk.LEFT, padx=10)
        
        # Screenshot button
        self.screenshot_btn = ttk.Button(main_frame, text="📸 Take Screenshot & Analyze", 
                                       command=self.take_screenshot_and_analyze, style="Accent.TButton")
        self.screenshot_btn.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to take screenshot")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        
        # Results table
        columns = ("Timestamp", "Filename", "Type", "Status", "AI Score", "Confidence")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
        
        column_widths = {"Timestamp": 130, "Filename": 150, "Type": 80, "Status": 120, "AI Score": 80, "Confidence": 80}
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="📁 Open Screenshots Folder", 
                  command=self.open_screenshots_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="💾 Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🗑️ Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def take_screenshot_fullscreen(self):
        """Take a full screen screenshot"""
        screenshot = pyautogui.screenshot()
        return screenshot, "fullscreen"
    
    def take_screenshot_area(self):
        """Take a screenshot of selected area"""
        try:
            # First, take a screenshot to use as overlay
            temp_screenshot = pyautogui.screenshot()
            
            # Hide this window temporarily
            self.root.withdraw()
            
            # Wait a moment for window to hide
            import time
            time.sleep(0.2)
            
            # Create area selector
            selector = AreaSelector(temp_screenshot)
            selected_area = selector.get_selection()
            
            # Show this window again
            self.root.deiconify()
            
            if selected_area:
                x1, y1, x2, y2 = selected_area
                # Take screenshot of selected area
                screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
                return screenshot, "area"
            else:
                return None, None
                
        except Exception as e:
            self.root.deiconify()  # Make sure window is visible again
            raise e
    
    def take_screenshot_and_analyze(self):
        """Take screenshot and analyze with Reality Defender in a separate thread"""
        def process():
            try:
                mode = self.screenshot_mode.get()
                self.update_status(f"Taking {'full screen' if mode == 'fullscreen' else 'area'} screenshot...")
                self.progress.start()
                self.screenshot_btn.config(state="disabled")
                
                # Take screenshot based on mode
                if mode == "fullscreen":
                    screenshot, screenshot_type = self.take_screenshot_fullscreen()
                else:  # area
                    screenshot, screenshot_type = self.take_screenshot_area()
                
                if screenshot is None:
                    self.update_status("Screenshot cancelled")
                    return
                
                # Save screenshot
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"screenshot_{screenshot_type}_{timestamp}.png"
                filepath = os.path.join(self.screenshots_folder, filename)
                screenshot.save(filepath)
                
                self.update_status("Screenshot saved. Analyzing with Reality Defender...")
                
                # Analyze with Reality Defender
                result = self.rd_client.detect_file(filepath)
                
                # Process results
                status = result.get('status', 'UNKNOWN')
                score = result.get('score', 0)
                confidence = self.get_confidence_level(score)
                
                # Add to results
                result_data = {
                    'timestamp': timestamp,
                    'filename': filename,
                    'filepath': filepath,
                    'screenshot_type': screenshot_type,
                    'status': status,
                    'score': score,
                    'confidence': confidence,
                    'full_result': result
                }
                
                self.analysis_results.append(result_data)
                
                # Update GUI
                self.root.after(0, lambda: self.add_result_to_table(result_data))
                self.root.after(0, lambda: self.update_status(f"Analysis complete: {status} (Score: {score:.2f})"))
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.root.after(0, lambda: self.update_status(error_msg))
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            
            finally:
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.screenshot_btn.config(state="normal"))
        
        # Run in separate thread to prevent GUI freezing
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def get_confidence_level(self, score):
        """Convert score to confidence level"""
        if score >= 0.8:
            return "High"
        elif score >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def add_result_to_table(self, result_data):
        """Add analysis result to the table"""
        values = (
            result_data['timestamp'],
            result_data['filename'],
            result_data['screenshot_type'].upper(),
            result_data['status'],
            f"{result_data['score']:.3f}",
            result_data['confidence']
        )
        
        item = self.results_tree.insert("", tk.END, values=values)
        
        # Color coding based on status
        if result_data['status'] == 'MANIPULATED':
            self.results_tree.set(item, "Status", "🚨 AI DETECTED")
        elif result_data['status'] == 'AUTHENTIC':
            self.results_tree.set(item, "Status", "✅ AUTHENTIC")
        
        # Scroll to the new item
        self.results_tree.see(item)
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def open_screenshots_folder(self):
        """Open the screenshots folder in file explorer"""
        try:
            os.system(f'open "{os.path.abspath(self.screenshots_folder)}"')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")
    
    def export_results(self):
        """Export results to JSON file"""
        if not self.analysis_results:
            messagebox.showwarning("No Data", "No results to export")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Results As"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export results: {e}")
    
    def clear_results(self):
        """Clear all results"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all results?"):
            self.analysis_results.clear()
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            self.update_status("Results cleared")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def create_gui():
    """Create and run the GUI application"""
    app = ScreenshotAnalyzer()
    app.run()

if __name__ == "__main__":
    create_gui()
# client = RealityDefender(api_key="rd_d3d3eac041426e52_1cb3a26dc710d98f1603883f38e51753")
# result = client.detect_file("/Users/jameszhao/Desktop/VIrtual Shield/download.jpg")

# data = {'request_id': '8555223c-dbc9-472d-8338-e154eca43ae4', 'status': 'MANIPULATED', 'score': 0.83, 'models': 
# [{'name': 'rd-oak-img', 'status': 'AUTHENTIC', 'score': 0.3051716387271881}, {'name': 'rd-context-img', 'status': 'MANIPULATED', 'score': 0.93}, 
# {'name': 'rd-img-ensemble', 'status': 'MANIPULATED', 'score': 0.7190354358368887}, 
# {'name': 'rd-elm-img', 'status': 'MANIPULATED', 'score': 0.975812554359436}, 
# {'name': 'rd-cedar-img', 'status': 'AUTHENTIC', 'score': 0.01}, 
# {'name': 'rd-pine-img', 'status': 'AUTHENTIC', 'score': 0.18169282376766205}]}
