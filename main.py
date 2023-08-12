from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain,LLMChain
from langchain.prompts import PromptTemplate,ChatPromptTemplate,HumanMessagePromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser

from services import get_youtube_transcript
from model import Translate,SqlGenerator,Summerize,PromptGenerator,BusinessName,Chat
from settings import origins


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up OpenAI API credentials

@app.get("/")
def read_root():
    return {"answer": "welcome to my AI build"}


@app.post("/api/chat")
def chat(message:Chat):
    load_dotenv()

    llm = ChatOpenAI(temperature=1)
    chain = ConversationChain(llm=llm)
    answer = chain.predict(input=message.message)
    return answer


@app.post("/api/translate")
def translate(detail:Translate):

    print(f'message:{detail.message}')
    load_dotenv()

    template = """Translate the following text : {message} from {from_language} to {to_language}:"""

    translation_prompt = PromptTemplate(
        input_variables=["message", "from_language","to_language"], template=template
    )

    llm = ChatOpenAI(temperature=0, max_tokens=500, model="gpt-3.5-turbo")
    chain = LLMChain(llm=llm, prompt=translation_prompt, verbose=True)

    response = chain.run(message=detail.message, from_language=detail.from_language,to_language=detail.to_language)

    return response

@app.post("/api/ytsummerize")
async def youtube_video_summerizer(detail:Summerize):
    print(f'url:{detail.youtube_url}')
    load_dotenv()
    docs=get_youtube_transcript(url=detail.youtube_url)
    return docs
    
    
@app.post("/api/business_name_generator")
def AI_business_name_generator(detail:BusinessName):
    output_paser=CommaSeparatedListOutputParser()
    format_instructions=output_paser.get_format_instructions()
    print(detail)

    load_dotenv()

    template = """List 20 uqnuie business name in the "{industry}" industy, with this list of Keywords:"{keywords}" .return only the names and nothing else. \n\n {format_instructions}"""

    prompt = ChatPromptTemplate(
       messages=[HumanMessagePromptTemplate.from_template(template=template)],
        input_variables=["keywords","industry"], 
        partial_variables={"format_instructions":format_instructions}
    )

    _input=prompt.format_messages(keywords=detail.keyword,industry=detail.industry)

    model = ChatOpenAI(temperature=0, max_tokens=200, model="gpt-3.5-turbo")
    #model = OpenAI(temperature=0)
    #chain = LLMChain(llm=llm, prompt=translation_prompt, verbose=True)

    #response = chain.run(keywords=detail.keyword,industry=detail.industry)
    output=model(_input)
    response=output_paser.parse(output.content)

    print(response)

    return response


@app.post("/api/sql_generator")
def generate_sql_code(text:SqlGenerator):
    load_dotenv()

    template = """You are an SQL query assistant.create an SQL query from this "{text}" """

    prompt = PromptTemplate(
        input_variables=["text"], template=template
    )

    llm = ChatOpenAI(temperature=0, max_tokens=200, model="gpt-3.5-turbo")
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

    response = chain.run(text=text.detail)

    return response

@app.post("/api/prompt_generator")
def generate_prompt(detail:PromptGenerator):
    load_dotenv()

    template = """your a helpful CHATGPT prompt specialist, create prompt for this task: "{detail}".indicate what has to be modified if any. return only the generated prompt and nothing else. """

    prompt = PromptTemplate(
        input_variables=["detail"], template=template
    )

    llm = ChatOpenAI(temperature=0.7, max_tokens=200, model="gpt-3.5-turbo")
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

    response = chain.run(detail=detail.detail)

    return response
