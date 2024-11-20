import Web3 from 'web3';

// Use the correct network URL for Sepolia test network
const ethNetwork = 'https://sepolia.infura.io/v3/2a195169b77c4532a9660754f9d15905';
const networks = {
  eth: new Web3(ethNetwork)
};

// Function to check the balance
const checkBalance = async (network, address) => {
  try {
    const balance = await networks[network].eth.getBalance(address);
    return networks[network].utils.fromWei(balance, 'ether');  // Return only the balance
  } catch (error) {
    throw new Error(`Error fetching balance for ${network}: ${error.message}`);
  }
};

// Main function to handle command line execution
const main = async () => {
  const [network, address] = process.argv.slice(2);

  // Validate the network input
  if (!networks[network]) {
    console.error('Invalid network. Choose "eth".');
    process.exit(1);
  }

  // Validate the address input
  if (!networks[network].utils.isAddress(address)) {
    console.error('Invalid address provided.');
    process.exit(1);
  }

  const balance = await checkBalance(network, address);
  console.log(balance);  // Output only the balance
};

// Run the main function directly if the module is being executed
main().catch(error => {
  console.error(error);
  process.exit(1);
});
