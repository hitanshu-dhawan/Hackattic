---
url: https://hackattic.com/challenges/brute_force_zip
code_url: https://github.com/hitanshu-dhawan/Hackattic
---

# Brute force ZIP

Grab the `zip_url` from the problem endpoint, download the ZIP file. Inside, among other things that you can rummage through, is a file called `secret.txt` which contains the solution to this challenge. But the ZIP is password protected, and I'm not giving you the password.

The password is between 4-6 characters long, lowercase and numeric. ASCII only.

You'll probably need to brute-force your way to the `secret.txt` file. Oh, and you have 30 seconds until the problem expires.

Go! Use the force!

##### Getting the problem set

`GET /challenges/brute_force_zip/problem?access_token=<access_token>`

Problem JSON will contain only one key:

- `zip_url`: the one-time URL for the ZIP file you'll need to brute-force

##### Submitting a solution

`POST /challenges/brute_force_zip/solve?access_token=<access_token>`

Solution JSON structure:

- `secret`: the secret value you found inside the `secret.txt` file

##### Why this challenge?

It occurred to me I never really looked into what the ZIP format is. Is there a spec? Is it proprietary? How does it encrypt stuff? It's all [pretty cool](https://en.wikipedia.org/wiki/Zip_\(file_format\)).

So until I come up with a challenge that deals with the format directly, here's a throwback to the one time we all forgot a ZIP password. Or... downloaded something with a password.

PS. I swear the name of this challenge sounds like a grunge/metal/post-punk/nu-rock band.

---
# Solution

... #Todo 

---
# Resources

- 


#Hackattic
