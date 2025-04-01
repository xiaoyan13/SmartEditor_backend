from ..AImodels.erniebot import erniebot

def generate_overview(text):
  prompt = f'''
  given the following text: """{text}"""
  Generate an abstract for it that tells in maximum 3 lines what is it about and use high level terms that will capture the main points,
  Use terms and words that will be most likely used by average person.
  '''
  return erniebot.ChatCompletion.create(model="ernie-4.0",
                                          messages=[
                                            {"role": "user", "content": prompt}
                                          ],
                                          stream=False)



def generate_faq(text):
  prompt = f'''
  given the following text: """{text}"""
  Ask relevant simple atomic questions ONLY (don't answer them) to cover all subjects covered by the text. Return the result as a json list example [q1, q2, q3...]
  '''
  return erniebot.ChatCompletion.create(model="ernie-4.0",
                                          messages=[
                                            {"role": "user", "content": prompt}
                                          ],
                                          stream=False)