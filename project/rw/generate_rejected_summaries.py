import json
from tqdm import tqdm
from transformers import T5Tokenizer, T5ForConditionalGeneration


d = json.load(open("../../data/rw.json"))

model_name = "google/flan-t5-xl"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name, device_map="auto", load_in_8bit=True)
h = open("saved_summaries.json", "w")
h.write('{"texts": [')
print("Generate for train...")
rejected = []
for line, acc in tqdm(zip(d["x_train"], d["y_train"]), total=len(d["x_train"])):
    prompt = "Summary: {0}".format(line)
    input_ids = tokenizer(prompt, padding="max_length", max_length=512, truncation=True, return_tensors="pt").input_ids.to("cuda")

    outputs = model.generate(input_ids, penalty_alpha=0.6, top_k=4, max_length=512)
    out = tokenizer.decode(outputs[0])#.replace("<pad>", "")
    print(out)
    #print("VS")
    #print(y_t)
    #print("----------------------------------------------------")
    rejected.append(out)
    h.write('{ "accepted": "'+acc.replace('\n', ' ').replace('"', ' ').replace("'", " ")+'", "rejected": "'+out.replace('\n', ' ').replace('"', ' ').replace("'", " ")+'"},\n')
h.write(']}')

d["train_rejected"] = rejected
h = open("")
print("Generate for validation...")
rejected = []
for line in tqdm(d["x_val"]):
    prompt = "Summary: {0}".format(line)
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")

    outputs = model.generate(input_ids, penalty_alpha=0.6, top_k=4, max_length=512)
    out = tokenizer.decode(outputs[0]).replace("<pad>", "")
    rejected.append(out)
    print("AVEM", out)

d["val_rejected"] = rejected

#g = open("dats.json", "w")
#json.dump(d, g)