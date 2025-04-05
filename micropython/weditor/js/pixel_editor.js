// Pixel Editor for RGB565 images
function openPixelEditor() {
    // Create modal dialog
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    // Create editor content
    const content = document.createElement('div');
    content.style.cssText = `
        background: #1e1e1e;
        padding: 20px;
        border-radius: 8px;
        color: white;
        font-family: 'Arial', sans-serif;
    `;
    
    content.innerHTML = `
        <div style="display: flex; gap: 20px; align-items: start;">
            <div>
                <div style="margin-bottom: 10px; font-size: 14px;">32x32 Pixel Editor</div>
                <canvas id="pixel-canvas" width="32" height="32" style="
                    border: 2px solid #333;
                    image-rendering: pixelated;
                    width: 320px;
                    height: 320px;
                    background: white;
                "></canvas>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <input type="color" id="pixel-color" value="#000000" style="
                    width: 100%;
                    height: 40px;
                    padding: 0;
                    border: none;
                    cursor: pointer;
                ">
                <button id="pixel-clear" style="
                    padding: 8px 16px;
                    margin: 4px;
                    border: none;
                    border-radius: 4px;
                    background: #0000ff;
                    color: black;
                    font-family: 'Arial', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                ">CLEAR</button>
                <button id="pixel-save" style="
                    padding: 8px 16px;
                    margin: 4px;
                    border: none;
                    border-radius: 4px;
                    background: #00ff00;
                    color: black;
                    font-family: 'Arial', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                ">SAVE AS LOGO.BIN</button>
                <button id="pixel-cancel" style="
                    padding: 8px 16px;
                    margin: 4px;
                    border: none;
                    border-radius: 4px;
                    background: #ff0000;
                    color: black;
                    font-family: 'Arial', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                ">CANCEL</button>
            </div>
        </div>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Add hover effect to buttons
    const buttons = content.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            button.style.opacity = '0.8';
        });
        button.addEventListener('mouseout', () => {
            button.style.opacity = '1';
        });
    });
    
    // Setup canvas
    const canvas = document.getElementById('pixel-canvas');
    const ctx = canvas.getContext('2d');
    const colorPicker = document.getElementById('pixel-color');
    
    // Fill with white initially
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, 32, 32);
    
    let isDrawing = false;
    
    // Convert mouse coordinates to canvas pixel coordinates
    function getPixelPos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: Math.floor((e.clientX - rect.left) * 32 / rect.width),
            y: Math.floor((e.clientY - rect.top) * 32 / rect.height)
        };
    }
    
    // Draw single pixel
    function drawPixel(x, y) {
        if (x < 0 || x >= 32 || y < 0 || y >= 32) return;
        ctx.fillStyle = colorPicker.value;
        ctx.fillRect(x, y, 1, 1);
    }
    
    // Mouse event handlers
    canvas.addEventListener('mousedown', (e) => {
        isDrawing = true;
        const pos = getPixelPos(e);
        drawPixel(pos.x, pos.y);
    });
    
    canvas.addEventListener('mousemove', (e) => {
        if (!isDrawing) return;
        const pos = getPixelPos(e);
        drawPixel(pos.x, pos.y);
    });
    
    canvas.addEventListener('mouseup', () => isDrawing = false);
    canvas.addEventListener('mouseleave', () => isDrawing = false);
    
    // Clear button
    document.getElementById('pixel-clear').onclick = () => {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, 32, 32);
    };
    
    // Cancel button
    document.getElementById('pixel-cancel').onclick = () => {
        modal.remove();
    };
    
    // Save button
    document.getElementById('pixel-save').onclick = () => {
        // Ask for filename
        const filename = prompt("Save as (without extension):", "logo");
        if (!filename) return;  // User cancelled
        
        // Convert canvas to RGB565 binary
        const imageData = ctx.getImageData(0, 0, 32, 32);
        const pixels = imageData.data;
        const binary = new Uint8Array(4 + 32 * 32 * 2); // Header + pixel data
        
        // Write header (32x32, big-endian)
        binary[0] = 0x00;
        binary[1] = 0x20; // 32 in hex
        binary[2] = 0x00;
        binary[3] = 0x20; // 32 in hex
        
        // Convert RGB888 to RGB565
        for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i];
            const g = pixels[i + 1];
            const b = pixels[i + 2];
            
            // RGB565 conversion
            const rgb565 = ((r & 0xF8) << 8) | // 5 bits red
                        ((g & 0xFC) << 3) | // 6 bits green
                        (b >> 3);           // 5 bits blue
            
            const pos = 4 + (i/4) * 2; // Header + pixel position
            binary[pos] = (rgb565 >> 8) & 0xFF; // High byte
            binary[pos + 1] = rgb565 & 0xFF;    // Low byte
        }
        
        // Save file using web editor's save mechanism
        const filepath = `/images/${filename}.bin`;
        fetch('/savefileb', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/octet-stream',
                'File-Path': filepath
            },
            body: binary
        })
        .then(response => response.json())
        .then(data => {
            showNotification(`Image saved as ${filepath}`, 1);
            modal.remove();
            loadDirPath(window.activeFileDir); // Refresh file list
        })
        .catch(error => {
            showNotification("Error saving image: " + error, 4);
        });
    };
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
} 