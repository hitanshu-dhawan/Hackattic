---
url: https://hackattic.com/challenges/touch_tone_dialing
code_url: https://github.com/hitanshu-dhawan/Hackattic
---

# Touch-Tone dialing

And now for something old-school cool...

You'll need to download a small `.wav` file with a [DTMF](https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling)-encoded sequence inside. Play it back, you'll hear it. The task is simple: decode the sequence and send it back as the solution.

The sequence only uses the `0-9` digits as well as `*` and `#`.

Good luck!

##### Getting the problem set

`GET /challenges/touch_tone_dialing/problem?access_token=<access_token>`

Problem JSON will contain only one key:

- `wav_url`: the one-time URL for the `.wav` file containing the encoded DTMF sequence

##### Submitting a solution

`POST /challenges/touch_tone_dialing/solve?access_token=<access_token>`

Solution JSON structure:

- `sequence`: the decoded DTMF sequence, as a string - e.g. `"*767#111239*55"`

##### Why this challenge?

Because you needed a reason to go rewatch [this cheesy masterpiece](https://www.imdb.com/title/tt0113243/). You're welcome!

---
# Solution

#Todo : Understand how the code is working...

