// Import Web3
import Web3 from 'web3';

// Create a new Web3 instance using the Infura endpoint
const web3 = new Web3('https://ropsten.infura.io/v3/2a195169b77c4532a9660754f9d15905');

// Generate a new wallet address
const createWallet = () => {
    const account = web3.eth.accounts.create();
    console.log('Address:', account.address);
    console.log('Private Key:', account.privateKey);
};

createWallet();
