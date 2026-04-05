# main.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
import logging
from ui import NovelGeneratorGUI
from automation_integration import integrate_automation_features

# 配置日志
logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    app = ctk.CTk()
    gui = NovelGeneratorGUI(app)
    
    # 集成自动化功能
    try:
        automation = integrate_automation_features(gui)
        if automation:
            logging.info("Automation features integrated successfully")
            # 将自动化实例保存到GUI中以便后续访问
            gui.automation = automation
        else:
            logging.warning("Failed to integrate some automation features")
    except Exception as e:
        logging.error(f"Error integrating automation features: {e}")
    
    app.mainloop()

if __name__ == "__main__":
    main()
