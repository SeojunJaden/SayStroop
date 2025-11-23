# SayStroop 

## Overview
SayStroop is a website testing a new aspect of the Stroop effect on participants. The goal of this website is to highlight the interference of automatic processing on controlled tasks through the Stroop effect. The website was built using Streamlit with integration of OpenAI's Whisper and Web-RTC for speech recognition. 

## Usage
Participants will visit the website and read a brief description of the Stroop effect. If participants consent to the experiment, we will keep their name and a given special ID. Once a participant enters their information they will encounter a 5 second timer prompting them to get ready, afterwards the experiment will begin. Participants will have to manually activate their microphone to begin the voice recording. During the experiment participants will read all words/colors in "incongruent" font. The experiment has two trials, one in which participants read the word and the second being where they read the font color. After a certain number of trials the experiment will conclude and the website will thank the participant for their time. For more details, visit the final research paper.

## Data Collection
| Reading Word | Reading Color of Font |
|--------------|----------------------|
| <br><br>     | <br><br>             |
| <br><br>     | <br><br>             |
| <br><br>     | <br><br>             |
| <br><br>     | <br><br>             |
| <br><br>     | <br><br>             |

In our experiment we had two trials to extract data from. With trial one, our participant is essentially reading the word being present to them (NOT the font color). Trial one serves as the baseline of our project, demonstrating how reading processes faster since it is highly automated. In trial two, our participant will instead be reading the font color instead of the actual word. In this trial participants will likely have a slower reaction time as they have to process the font color instead of reading the word directly. This highlights the difference between automated and controlled responses as participants will take more time needing to process the difference in word meaning and font color. 

## Aspects
- Interactive testing
- Participant information storage
- Automatic speech recognition
- Data collection
- Analysis

## Limitations and Future Improvements
- As of now, SayStroop is simply testing the validity of the Stroop effect, with deeper research and thought we could explore more complex tests with the Stroop effect.
- Fine tuning OpenAI's Whisper so that participants have a greater user friendly experience.
- Redesign of SayStroop, the current aestheic is simplistic and concise, in future iterations we could try something more bold.
- We could expand our range of sampling, as of now we are primarily sampling participants based in the San Diego area. 

## Resources & Help
- Streamlit
- Web-RTC
- Supabase
- OpenAI's Whisper
- Generative AI: ChatGPT, Claude, VO
