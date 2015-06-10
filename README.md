#Save to Give

What’s your guilty pleasure? Pricey cappuccinos? That extra beer? Dinners out that always end up being more expensive than you expected? Choosing to make dinner at home with friends or drink ordinary brewed coffees a couple times per week can save you enough money to donate malaria treatment packages for children, bushels of seeds for farmers, or even low-cost, energy saving stoves. Accept a challenge from Save to Give and log progress towards meeting your goal of saving up to donate to families in need. Your small lifestyle changes can make a huge difference. Save to give. Give to save.


####Technology Stack
Python, Flask, Jinja, SQLAlchemy, SQLite, MintAPI, JavaScript, jQuery, Underscore, AJAX, HTML, CSS, BootStrap


![image](/static/images/homepage.jpg) 


####Using Save to Give

Build your own challenges by selecting something you spend too much money on and Save to Give will provide you with an alternative. Challenges are highly customizable, so you get to decide how many times you will substitute one item for another. The dynamic "Add a new challenge" form sends your choices back to the server with multiple AJAX calls and calculates an estimate of how much money you will save. It matches the estimate with donation items in the database and gives you the three closest matches, allowing you to accept one of those challenges or adjust your previous input and get a new set of donation items.

The donation items are carefully selected from reputable organizations that have gift-giving donation programs - donate a specific amount that goes directly to buying something tangible for a family in need, such as farming supplies, necessary household items, or even livestock.

Here are some examples of challenges and corresponding donation items:

![image](/static/images/challenge_examples.jpg) 

Save to Give tracks your progress towards completing challenges and displays line charts of cumulative progress for easy visual reference. Update your progress through another dynamic form that asks you how many times you've substituted the alternative, cheaper item. It estimates how much you've saved, and allows you to edit that estimate. When cumulative progress reaches the donation target, Save to Give prompts the user to donate.

![image](/static/images/Profile.jpg) 


You can also ask Save to Give to send you customized challenges based on an analysis of your spending habits. I use a Mint screenscraping python library, called MintAPI, that gathers a user's transactions into relevant buckets (ignoring categories like "rent" and "federal tax"), and runs the spending buckets through some logic on the backend to figure out where a user could cut back. To make sure users' financial data is secure, I do not store any of their Mint information in my database. Every time they want to access the transaction analysis page, they login with their Mint username and password. Calculations are performed immediately, and the results are shown on the graph so that none of their transaction data needs to be stored.

![image](/static/images/TransactionAnalysis.jpg) 


#### Ideas for Scaling Up

#####Social:
* Challenge a friend
* Pay a friend back by accepting a challenge and donating the amount you owe
  * Possibly incorporate Kiva - make a microfinance investment for the friend you owe. She can then wait a little while before collecting the amount and allow the kiva entrepreneur to use the funding.
* Levels for users with different kinds of donation items and possibly higher amounts.
* Accountability feed for tracking friends' progress - especially if you're sending each other challenges!

#####Transaction Analysis
* More rigorous transaction analysis and challenge-matching based on aggregated Mint data from many users. Transaction analysis will get more and more accurate if more users opt to have their Mint data analyzed.
* Studying whether users adjust Save to Give's estimate of how much they saved when they update their progress will gradually make Save to Give's estimates of the cost of individual items more accurate.

#####Payment Gateway
* Payment gateway that allows users to donate directly through Save to Give's website instead of linking to the organization's site.

