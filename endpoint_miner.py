import argparse
import bittensor
from typing import List, Dict
import requests
import json
import traceback
import time

class EndpointMiner( bittensor.BasePromptingMiner ):

    @classmethod
    def check_config( cls, config: 'bittensor.Config' ):
        pass

    @classmethod
    def add_args( cls, parser: argparse.ArgumentParser ):
        parser.add_argument( '--endpoint.verify_token', type=str, help='Auth' )
        parser.add_argument( '--endpoint.url', type=str, help='Endpoint' )

        
    def __init__( self ):
        super( EndpointMiner, self ).__init__()
        print ( self.config )
    
        
    def forward(self, messages: List[Dict[str, str]]) -> str:
        start_time=time.time()
        generation = "An error occured with the miner and it is not available now."
        
        try:
            for i, item in enumerate(messages):
                if type(item) == str:
                    messages[i] = json.loads(item)
            
            response = requests.post(self.config.endpoint.url, data=json.dumps({"messages": messages, "verify_token":self.config.endpoint.verify_token}), headers= {"Content-Type": "application/json"}, timeout=9.5)
            
            generation = response.json()["response"]
            
        except Exception as e:
            traceback.print_exc()
            print("Error", e)
            print("Response", response.json())
            print("Errored messages", messages,"\n")
            
        print("messages:", messages)
        print("Generation:", generation)
        time_to_sleep = 9.5 - (time.time()-start_time)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
        return generation

if __name__ == "__main__":
    bittensor.utils.version_checking()
    EndpointMiner().run()
