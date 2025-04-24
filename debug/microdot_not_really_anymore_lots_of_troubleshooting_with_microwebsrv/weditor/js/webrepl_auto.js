// Auto-connect to WebREPL with empty password
(function() {
    // Configure terminal font size
    const terminalStyle = document.createElement('style');
    terminalStyle.textContent = `
        .terminal {
            font-family: monospace;
            font-size: 14px !important;
            line-height: 17px !important;
        }
    `;
    document.head.appendChild(terminalStyle);

    // Wait for terminal to be initialized
    const termCheck = setInterval(() => {
        if (typeof term !== 'undefined' && term) {
            clearInterval(termCheck);
            
            // Hook into terminal's write method
            const originalWrite = term.write.bind(term);
            term.write = function(data) {
                originalWrite(data);
                
                // Force scroll after a tiny delay to let content render
                setTimeout(() => {
                    const terminal = document.querySelector('#term .terminal');
                    if (terminal) {
                        // Get all content divs and filter out empty ones
                        const contentDivs = Array.from(terminal.querySelectorAll('div > div')).filter(div => {
                            // Get text content without extra spaces
                            const text = div.textContent.trim();
                            // Consider div empty if it's just spaces or empty
                            return text.length > 0 && !text.match(/^\s+$/);
                        });
                        
                        if (contentDivs.length > 0) {
                            // Scroll to last non-empty div
                            const lastDiv = contentDivs[contentDivs.length - 1];
                            lastDiv.scrollIntoView(false);
                        }
                    }
                }, 10);
            };
        }
    }, 100);
    
    // Check periodically if WebSocket is available
    const wsCheck = setInterval(() => {
        if (typeof ws !== 'undefined' && ws) {
            clearInterval(wsCheck);
            
            // Hook into onopen to send Enter key after connection
            const originalOnOpen = ws.onopen;
            ws.onopen = function(event) {
                if (originalOnOpen) {
                    originalOnOpen.call(ws, event);
                }
                // Wait a bit for welcome message then send Enter
                setTimeout(() => {
                    ws.send('\r');
                }, 500);
            };
        }
    }, 100);
})(); 