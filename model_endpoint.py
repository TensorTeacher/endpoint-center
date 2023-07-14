
import os
import argparse
from typing import Dict, List
from flask import Flask, request, jsonify
import json
import random
import traceback
import sys
import time
import requests
import re
import copy
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run API with OpenAI parameters.")
    parser.add_argument("--auth_token", default="", help="Authentication token")
    parser.add_argument("--model_name", default="gpt-3.5-turbo", help="Model name")
    parser.add_argument("--port", default=8008, type=int, help="Model name")
    return parser.parse_args()


# Define the Flask app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def chat():
    # Check authentication token
    request_data = request.get_json()
    auth_token = request_data.get("verify_token")
    if auth_token != args.auth_token:
        return jsonify({"error": "Invalid authentication token"}), 401

    # Get messages from the request
    
    messages = request_data.get("messages", [])
    n = request_data.get('n', 1)

    # Call the forward function and get the response
    try:
        response = miner.forward(messages, num_replies = n)
    except:
        traceback.print_exc(file=sys.stderr)
        return "An error occured"
    if len(response) == 1:
        response = response[0]
    # Return the response
    return jsonify({"response": response})



class ModelMiner():

    def __init__( self, model_name, device="cuda", max_length=250, temperature=0.7, do_sample=True ):
        super( ModelMiner, self ).__init__()
        
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        self.do_sample = do_sample
        
        self.system_prompt=""

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False )
        self.model = AutoModelForCausalLM.from_pretrained( model_name, torch_dtype = torch.float16, low_cpu_mem_usage=True )
        print("model loaded")
        
        
        if self.device != "cpu":
            self.model = self.model.to( self.device )

    def _process_history(self, history: List[str]) -> str:
        processed_history = ''

        if self.system_prompt:
            processed_history += self.system_prompt

        for message in history:
            if message['role'] == 'system':
                processed_history += '' + message['content'].strip() + ' '

            if message['role'] == 'assistant':
                processed_history += 'ASSISTANT:' + message['content'].strip() + '</s>'
            if message['role'] == 'user':
                processed_history += 'USER: ' + message['content'].strip() + ' '
        return processed_history

    def forward(self, messages, num_replies=4):

        history = self._process_history(messages)
        prompt = history + "ASSISTANT:"

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        # output = self.model.generate(
        #     input_ids,
        #     max_length=input_ids.shape[1] + self.max_length,
        #     temperature=self.temperature,
        #     do_sample=self.do_sample,
        #     pad_token_id=self.tokenizer.eos_token_id,
        # )

        # generation = self.tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
        output = self.model.generate(
            input_ids,
            max_length=input_ids.shape[1] + self.max_length,
            temperature=self.temperature,
            do_sample=self.do_sample,
            pad_token_id=self.tokenizer.eos_token_id,
            num_return_sequences=num_replies,  # Set the number of desired replies
            # penalty_alpha=0.6, top_k=4,
        )
        
        generations = []
        for sequence in output:
            generation = self.tokenizer.decode(sequence[input_ids.shape[1]:], skip_special_tokens=True)
            generations.append(generation)

        # Logging input and generation if debugging is active
        print("Message: " + str(messages),flush=True)
        print("Generation: " + str(generation),flush=True)

        return generations


if __name__ == "__main__":
    args = parse_arguments()
    miner = ModelMiner(args.model_name)
    app.run(host="0.0.0.0", port=args.port, threaded=False)
