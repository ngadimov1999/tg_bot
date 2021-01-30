# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 16:42:42 2020

@author: QickKer
"""

from selenium import webdriver
import random
import os
import zipfile

class Request:

    
    def __init__(self, url, use_proxy=False, user_agent=False):
        self.use_proxy = use_proxy
        self.user_agent = user_agent
        driver = self.get_chromedriver()
            
            
            
    def myProxy(self):
        proxies = []
        with open('ip_port_username_pass.txt') as f:
            for line in f:
                proxies.append(line.strip())
        proxy = random.choice(proxies)
        return  proxy.split(':')

    def get_user_agent(self):
        user_agents = []
        with open ('ua.txt') as f:
            for line in f:
                user_agents.append(line.strip())
        return random.choice(user_agents)
    
    
    def get_chromedriver(self):
        if self.use_proxy:
            proxy_line = self.myProxy()
            self.host = proxy_line[0]
            self.port = proxy_line[1]
            self.user = proxy_line[2]
            self.pas = proxy_line[3]
       
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            
            background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                      },
                      bypassList: ["localhost"]
                    }
                  };
            
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
            
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (self.host, self.port, self.user, self.pas)
        
        path = os.path.dirname(os.path.abspath('chromedriver.exe'))
        chrome_options = webdriver.ChromeOptions()
        if self.use_proxy:
            pluginfile = 'proxy_auth_plugin.zip'
    
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            chrome_options.add_extension(pluginfile)
        if self.user_agent:
            chrome_options.add_argument('--user-agent=%s' % self.get_user_agent())
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('----disable-bundled-ppapi-flash')
        chrome_options.add_extension('webrtc.crx')
        self.driver = webdriver.Chrome(
            os.path.join(path, 'chromedriver'),
            options=chrome_options)
        self.driver.implicitly_wait(10)
        return self.driver
    
