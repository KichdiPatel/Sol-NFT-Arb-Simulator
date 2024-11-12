# Sol NFT Arbitrage Simulator

April 2024:

After researching the Solana ecosystem, I noticed that at some times there were consistent price differences on NFT collections that were not being botted, the same way they were being botted ethereum NFT collections. This was probably since it was a non-EVM chain and less MEV searchers on SOL at the time. So, I wanted to determine if there was a lucrative enough arbitrage opportunity on NFT's where building some type of arbitrage bot would be worth the effort. So, I decided to scrape Solana NFT Marketplaces and see if just based on that data, if there were any arbitrage opportunities. I specifically scraped Magic Eden and Tensor with the idea that if I could discover enough arbitrage opportunities between these two exchanges, then there would definetely also be opportunities when including other exchanges.

## The Code

The program has a dictionary of the popular Solana NFT collections at the time and their magic eden/tensor links. Then, each collection is iterated and the code scrapes the bid and ask price from both marketplace websites. For context, both marketplaces have systems where you can buy the lowest priced item and also sell to offers that other users make. So, I wanted to see if a flash arbitrage was present where I could buy on one exchange and then sell to a offer on the other exchange(where the offer is higher than the buy price).

## Conclusion

At the time there was surprisingly a decent amount of arbitrage opportunities that would pop up at least a few times a day on these collections. I did not end up developing an arbitrage bot, but it would be an interesting opportunitiy to look into on other chains that have mediocre-good NFT liquidity. It was definetely something that was not being botted, or they were at least not very optimized, since there was enough time if someone was aggressively watching, where you could manually capitalize on these opportunities. It is now November of 2024, and the spreads have drastically decreased between exchanges.

## Other Notes

This code may not work anymore as the html structures of the sites may have changed. \
Hope you enjoyed this writeup!
