// http://api.marketstack.com/v1/tickers
//     ? access_key = 29fd634def434ff2b690e5efefda8e40
//  ()
// import requests

// params = {
//   'access_key': 'YOUR_ACCESS_KEY'
// }

// api_result = requests.get('https://api.marketstack.com/v1/tickers/aapl/eod', params)

// api_response = api_result.json()

// for stock_data in api_response['data']:
//     print(u'Ticker %s has a day high of  %s on %s' % (
//       stock_data['symbol']
//       stock_data['high']
//       stock_data['date']
//     ))ate']
// ))
// http://api.marketstack.com/v1/tickers/${stock}?access_key=29fd634def434ff2b690e5efefda8e40
// http://api.marketstack.com/v1/eod?access_key=29fd634def434ff2b690e5efefda8e40&symbols=${stock}