import random
from datetime import datetime

sqli_vectors = ["' OR '1'='1", "UNION SELECT NULL", "admin' --"]
xss_vectors = ["<script>alert(1)</script>", "javascript:void(0)"]
user_agents = ["Mozilla/5.0", "BadBot/1.0", "Hydra/8.1"]

print("Generating web-server.log...")
with open("web-server.log", "w") as f:
    for i in range(100):
        is_attack = random.random() < 0.2
        ip = f"192.168.1.{random.randint(1, 255)}"
        time = datetime.now().isoformat()
        
        if is_attack:
            attack_type = random.choice(["SQLi", "XSS"])
            payload = random.choice(sqli_vectors if attack_type == "SQLi" else xss_vectors)
            log_line = f"{ip} - [{time}] \"GET /login?user={payload} HTTP/1.1\" 403 1024 \"{random.choice(user_agents)}\""
        else:
            log_line = f"{ip} - [{time}] \"GET /home HTTP/1.1\" 200 2048 \"Mozilla/5.0\""
        
        f.write(log_line + "\n")

print("Done! Upload 'web-server.log' to S3 later.")