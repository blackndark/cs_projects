-- Keep a log of any SQL queries you execute as you solve the mystery.

-- Theft took place on July 28, 2020 and that it took place on Chamberlin Street.

-- Starting investigation by checking the crime scene reports to see if there is any log about the crime that happened in July 28, 2020, on Chamberlin Street.
SELECT * FROM crime_scene_reports WHERE year = 2020 AND month = 7 AND day = 28 AND street = 'Chamberlin Street'

-- Log from the crime_scene_reports = Theft of the CS50 duck took place at 10:15am at the Chamberlin Street courthouse. Interviews were conducted today with three witnesses who were present at the time — each of their interview transcripts mentions the courthouse.

-- Pulling the interviews made that day to learn the comments of the three witneses.
SELECT name, transcript FROM interviews WHERE year = 2020 AND month = 7 AND day = 28

-- After reading the interviews we learn that one witness saw the thief get into a car sometime within 10 mins of the theft. So we are pulling name of the people who left the crime scene in the next 10 mins via their license plate.
SELECT name FROM people WHERE license_plate IN (SELECT license_plate FROM courthouse_security_logs WHERE year = 2020 AND month = 7 AND day = 28 AND hour = 10 AND minute > 15 AND minute <= 25 AND activity = 'exit')

-- We have 8 names who left the crime scene within 10 mins: Patrick, Amber, Elizabeth, Roger, Danielle, Russell, Evelyn, Ernest
-- Another witness saw the thief earlier at the day withdrawing money form an ATM. So we are checking if these people withdrew money in the morning on the crime day on Fifer Street by joining people, bank_accounts and atm_transactions.
SELECT name FROM atm_transactions
JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
JOIN people ON bank_accounts.person_id = people.id
WHERE name IN (SELECT name FROM people WHERE license_plate IN
(SELECT license_plate FROM courthouse_security_logs WHERE year = 2020 AND month = 7 AND day = 28 AND hour = 10 AND minute > 15 AND minute <= 25 AND activity = 'exit')
)
AND year = 2020 AND month = 7 AND day = 28 and atm_location = 'Fifer Street' AND transaction_type='withdraw'

-- By looking at the withdraw action from atm_transactions on the crime day on Fifer Street, we managed to decrease the suspects to 4 people: Ernest, Russell, Elizabeth, Danielle

-- We will look at the phone_calls table with the help of people table to see if any of those 4 people called to someone and talked to less than 1 minute on crime day.
SELECT name from people
JOIN phone_calls ON people.phone_number = phone_calls.caller
WHERE name IN (SELECT name FROM atm_transactions
JOIN bank_accounts ON atm_transactions.account_number = bank_accounts.account_number
JOIN people ON bank_accounts.person_id = people.id
WHERE name IN (SELECT name FROM people WHERE license_plate IN
(SELECT license_plate FROM courthouse_security_logs WHERE year = 2020 AND month = 7 AND day = 28 AND hour = 10 AND minute > 15 AND minute <= 25 AND activity = 'exit')
)
AND year = 2020 AND month = 7 AND day = 28 AND atm_location = 'Fifer Street' AND transaction_type='withdraw')
AND year = 2020 AND month = 7 AND day = 28 AND duration < 60

-- We found out that only 2 people in our list called to someone and talked to less than 1 minute on crime day: Ernest and Russell

-- We'll see who these 2 suspects talked to on the phone under 1 minute on crime day
SELECT name FROM people
JOIN phone_calls ON people.phone_number = phone_calls.receiver
WHERE phone_number IN (SELECT receiver FROM people
JOIN phone_calls ON people.phone_number = phone_calls.caller
WHERE name IN ('Ernest', 'Russell'))
AND year = 2020 AND month = 7 AND day = 28 AND duration < 60

-- Our suspects talked to Berthold and Philip on the phone under 1 minute on crime day

-- We'll join airports and flights to learn the earliest flight out of Fiftyville on 29th of July.
SELECT abbreviation, city, full_name FROM airports WHERE id IN (SELECT destination_airport_id FROM airports
JOIN flights ON airports.id = flights.origin_airport_id
WHERE origin_airport_id IN (SELECT id FROM airports WHERE city = 'Fiftyville')
AND year = 2020 AND month = 7 AND day = 29
ORDER BY hour, minute
LIMIT 1)

-- The earliest flight out of Fiftyville on 29 July is to London at 8:20AM. So the thief escaped to LONDON. Which has a destination_airport_id of 4.

-- We'll pull the passengers for the early morning London flight on 29 July and see if we find a match with our usual suspects Ernest and Russell, and our potential accomplices Berthold and Philip. Because we don't know on whose name they bought the tickets.
SELECT name from people 
WHERE passport_number IN (SELECT passport_number FROM passengers
JOIN flights ON passengers.flight_id = flights.id
WHERE destination_airport_id = 4
AND year = 2020 AND month = 7 AND day = 29 AND hour = 8 AND minute = 20)
AND name IN ('Ernest', 'Russell', 'Berthold', 'Philip')

-- With that we learn that they bought the tickets on Ernest's name. So we know that the thief is ERNEST, because he is one of our 2 usual suspects(Ernest and Russell).

-- Now we can check the phone call records and find out if the thief talked to one of our potential accomplices(Berthold and Philip).
SELECT name from people
WHERE phone_number IN (SELECT receiver from people
JOIN phone_calls ON people.phone_number = phone_calls.caller
WHERE name = 'Ernest'
AND year = 2020 AND month = 7 AND day = 28)
AND name IN('Berthold', 'Philip')

-- We learned that our thief Ernest talked to Berthold on the crime day. So the accomplice is BERTHOLD.
