Claude AI 

## First prompt

***https://github.com/MatyVic/HillelDjangoHW need code review tell strong and weak points***

## Second prompt

***Book.price is an IntegerField — money should be DecimalField (as correctly done in Order.total_price and OrderDetail.price). Mixing the two is inconsistent and risks rounding bugs.***
***Rating.rating has no validators (MinValueValidator/MaxValueValidator) — nothing stops a rating of -50 or 9999. There's also no unique_together on (book, user), so a user could submit unlimited ratings for the same book.***
***Cart.add_book/remove_book cast amount with int(amount) with no validation — a negative quantity or non-numeric string will either throw an uncaught exception or quietly corrupt the cart total. Cart quantities also aren't checked against Book.amount (stock) anywhere.***
***let's fix this give me your suggestions in the next thing. Show my code and give me your variant how you fix it***

## Third prompt

***let's cover app shop with test like in order app generate some tests and add comment #Test generated with AI before***
|END|

Gemini AI

## First prompt
***Cover shop/views.py with tests***