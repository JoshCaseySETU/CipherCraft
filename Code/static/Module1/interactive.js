function encryptCaesar(message, shiftAmount) {
    // Parse shiftAmount as an integer
    shiftAmount = parseInt(shiftAmount);

    // Check if shiftAmount is a valid number
    if (isNaN(shiftAmount)) {
        // If shiftAmount is not a valid number, return an error message
        return 'Error: Shift amount must be a valid number.';
    }

    // Check if message is a string
    if (typeof message !== 'string') {
        // If message is not a string, return an error message
        return 'Error: Message must be a string.';
    }

    // Convert the message to uppercase for simplicity
    message = message.toUpperCase();
    
    // Initialize an empty string to store the encrypted message
    let encryptedMessage = '';
    
    // Iterate through each character in the message
    for (let i = 0; i < message.length; i++) {
        const char = message[i];
        
        // Check if the character is a letter
        if (char.match(/[A-Z]/)) {
            // Get the ASCII code of the character
            let charCode = message.charCodeAt(i);
            
            // Apply the shift to the ASCII code
            charCode = ((charCode - 65 + shiftAmount) % 26) + 65;
            
            // Convert the ASCII code back to a character and append to the encrypted message
            encryptedMessage += String.fromCharCode(charCode);
        } else {
            // If the character is not a letter, keep it unchanged
            encryptedMessage += char;
        }
    }
    
    // Return the encrypted message
    return encryptedMessage;
}



function decryptCaesar(encryptedMessage, shiftAmount) {
    // Decrypting a Caesar cipher is essentially encrypting with a negative shift
    return encryptCaesar(encryptedMessage, -shiftAmount);
}

// Define function for frequency analysis
function frequencyAnalysis(encryptedMessage) {
    // Convert the message to uppercase for simplicity
    encryptedMessage = encryptedMessage.toUpperCase();
    
    // Initialize a string to store the frequency information
    let frequencyString = '';
    
    // Initialize an object to store the frequency of each letter
    const frequency = {};
    
    // Iterate through each character in the message
    for (let i = 0; i < encryptedMessage.length; i++) {
        const char = encryptedMessage[i];
        
        // Check if the character is a letter
        if (char.match(/[A-Z]/)) {
            // Increment the count for this letter in the frequency object
            frequency[char] = (frequency[char] || 0) + 1;
        }
    }
    
    // Convert the frequency object to a string
    for (const letter in frequency) {
        frequencyString += `${letter}: ${frequency[letter]}, `;
    }
    
    // Remove the trailing comma and space
    frequencyString = frequencyString.slice(0, -2);
    
    // Return the frequency information as a string
    return frequencyString;
}

// Define functions for Vigenère cipher encryption and decryption
function encryptVigenere(message, key) {
    // Convert the message and key to uppercase for simplicity
    if (message === undefined || message === null || key === undefined || key === null) {
        console.error('Error: Message or key is undefined or null.');
        return null; // Return null to indicate an error
    }
    
    // Check if message and key are strings
    if (typeof message !== 'string' || typeof key !== 'string') {
        console.error('Error: Message or key is not a string.');
        return null; // Return null to indicate an error
    }

    message = message.toUpperCase();
    key = key.toUpperCase();
    
    // Initialize an empty string to store the encrypted message
    let encryptedMessage = '';
    
    // Initialize a variable to keep track of the position in the key
    let keyIndex = 0;
    
    // Iterate through each character in the message
    for (let i = 0; i < message.length; i++) {
        const char = message[i];
        
        // Check if the character is a letter
        if (char.match(/[A-Z]/)) {
            // Get the ASCII code of the character
            let charCode = message.charCodeAt(i);
            
            // Get the ASCII code of the corresponding key character
            let keyCode = key.charCodeAt(keyIndex % key.length);
            
            // Apply the Vigenère cipher encryption formula
            charCode = ((charCode - 65 + keyCode - 65) % 26) + 65;
            
            // Increment the key index
            keyIndex++;
            
            // Convert the ASCII code back to a character and append to the encrypted message
            encryptedMessage += String.fromCharCode(charCode);
        } else {
            // If the character is not a letter, keep it unchanged
            encryptedMessage += char;
        }
    }
    
    // Return the encrypted message
    return encryptedMessage;
}

function decryptVigenere(encryptedMessage, key) {
    // Convert the key to uppercase for simplicity
    key = key.toUpperCase();
    
    // Initialize an empty string to store the decrypted message
    let decryptedMessage = '';
    
    // Initialize a variable to keep track of the position in the key
    let keyIndex = 0;
    
    // Iterate through each character in the encrypted message
    for (let i = 0; i < encryptedMessage.length; i++) {
        const char = encryptedMessage[i];
        
        // Check if the character is a letter
        if (char.match(/[A-Z]/)) {
            // Get the ASCII code of the character
            let charCode = encryptedMessage.charCodeAt(i);
            
            // Get the ASCII code of the corresponding key character
            let keyCode = key.charCodeAt(keyIndex % key.length);
            
            // Apply the Vigenère cipher decryption formula
            charCode = ((charCode - 65 - (keyCode - 65) + 26) % 26) + 65;
            
            // Increment the key index
            keyIndex++;
            
            // Convert the ASCII code back to a character and append to the decrypted message
            decryptedMessage += String.fromCharCode(charCode);
        } else {
            // If the character is not a letter, keep it unchanged
            decryptedMessage += char;
        }
    }
    
    // Return the decrypted message
    return decryptedMessage;
}

function encryptFence(message, numRails) {
    let rail = new Array(numRails).fill().map(() => []);

    let dirDown = false;
    let row = 0, col = 0;

    for (let i = 0; i < message.length; i++) {
        if (row === 0 || row === numRails - 1) dirDown = !dirDown;
        
        // Ensure that rail[row] is properly initialized
        if (!rail[row]) {
            rail[row] = [];
        }
        
        rail[row][col] = message[i];
        col++;

        // Adjust row based on direction
        row += dirDown ? 1 : -1;
    }

    // Concatenate rows to form the encrypted message
    let result = rail.flat().join('');

    return result;
}



function decryptFence(encryptedMessage, numRails) {
    let rail = new Array(numRails).fill().map(() => new Array(encryptedMessage.length).fill('\n'));
    let dir_down = false;
    let row = 0, col = 0;
   
    for (let i = 0; i < encryptedMessage.length; i++) {
      if (row == 0) dir_down = true;
      if (row == numRails - 1) dir_down = false;
      rail[row][col++] = '*';
      dir_down ? row++ : row--;
    }
   
    let index = 0;
    for (let i = 0; i < numRails; i++)
      for (let j = 0; j < encryptedMessage.length; j++)
        if (rail[i][j] == '*' && index < encryptedMessage.length) rail[i][j] = encryptedMessage[index++];
   
    let result = '';
    row = 0, col = 0;
    for (let i = 0; i < encryptedMessage.length; i++) {
      if (row == 0) dir_down = true;
      if (row == numRails - 1) dir_down = false;
      if (rail[row][col] != '*') result += rail[row][col++];
      dir_down ? row++ : row--;
    }
   
    return result;
}



