import Web3 from 'web3';

// Create a new Web3 instance using the opBNB testnet endpoint
const web3 = new Web3('https://opbnb-testnet.infura.io/v3/2a195169b77c4532a9660754f9d15905'); // Replace with your Infura project ID

// Function to send tokens from one address to another
const sendTokens = async (senderAddress, senderPrivateKey, recipientAddress, amount) => {
    try {
        // Convert amount to Wei (assuming amount is in Ether)
        const amountInWei = web3.utils.toWei(amount.toString(), 'ether');

        // Create the transaction object
        const transaction = {
            to: recipientAddress,
            value: amountInWei,
            gas: 2000000,
            gasPrice: await web3.eth.getGasPrice(),
            nonce: await web3.eth.getTransactionCount(senderAddress)
        };

        // Sign the transaction
        const signedTransaction = await web3.eth.accounts.signTransaction(transaction, senderPrivateKey);

        // Send the signed transaction
        const receipt = await web3.eth.sendSignedTransaction(signedTransaction.rawTransaction);
        
        console.log('Transaction successful with hash:', receipt.transactionHash);
    } catch (error) {
        console.error('Error sending tokens:', error);
    }
};

// Main function to execute token transfer
const main = async () => {
    const senderAddress = process.argv[2]; // First argument: sender address
    const senderPrivateKey = process.argv[3]; // Second argument: sender's private key
    const recipientAddress = process.argv[4]; // Third argument: recipient address
    const amount = process.argv[5]; // Fourth argument: amount to send

    if (!senderAddress || !senderPrivateKey || !recipientAddress || !amount) {
        console.log('Usage: node wat.mjs <senderAddress> <senderPrivateKey> <recipientAddress> <amount>');
        return;
    }

    await sendTokens(senderAddress, senderPrivateKey, recipientAddress, amount);
};

// Run the main function
main();
