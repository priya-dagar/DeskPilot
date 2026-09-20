"""
Seed data: the 15 employee requests and the existing ticket queue from the
Veridian Corp data pack (week of 21-25 Sep 2026). Used to pre-populate the
demo so a reviewer can pick a request and watch the agent work.
"""

EMPLOYEE_REQUESTS = [
    {"id": "REQ-01", "employee": "Aditi Sharma", "email": "aditi.sharma@veridiancorp.example",
     "date": "Mon 21 Sep", "text": "My laptop won't turn on at all, it's completely dead, had it about 3.5 years now.",
     "prior_action": "Not started"},
    {"id": "REQ-02", "employee": "Vikram Chawla", "email": "vikram.chawla@veridiancorp.example",
     "date": "Mon 21 Sep", "text": "Can I get Wi-Fi access for a guest visiting our office tomorrow?",
     "prior_action": "Not started"},
    {"id": "REQ-03", "employee": "Karan Mehta", "email": "karan.mehta@veridiancorp.example",
     "date": "Mon 21 Sep", "text": "I'm locked out of my account, tried my password 6 times.",
     "prior_action": "In progress - reset queued"},
    {"id": "REQ-04", "employee": "Ritu Bhatia", "email": "ritu.bhatia@veridiancorp.example",
     "date": "Tue 22 Sep", "text": "Need approval to install a data-analysis tool that's not in the software catalog.",
     "prior_action": "Waiting on Security review"},
    {"id": "REQ-05", "employee": "Sanjay Oberoi", "email": "sanjay.oberoi@veridiancorp.example",
     "date": "Tue 22 Sep", "text": "My VPN stopped working this morning, says credentials expired.",
     "prior_action": "Not started"},
    {"id": "REQ-06", "employee": "Meera Iyer", "email": "meera.iyer@veridiancorp.example",
     "date": "Tue 22 Sep", "text": "Printer on the 3rd floor keeps showing \"paper jam\" even though there's no jam.",
     "prior_action": "Investigating - technician assigned"},
    {"id": "REQ-07", "employee": "Farhan Ali", "email": "farhan.ali@veridiancorp.example",
     "date": "Wed 23 Sep", "text": "I've started working from home 4 days a week, how do I get a monitor?",
     "prior_action": "Not started"},
    {"id": "REQ-08", "employee": "Ananya Reddy", "email": "ananya.reddy@veridiancorp.example",
     "date": "Wed 23 Sep", "text": "I think I got a phishing email asking for my login - forwarding it to a few teammates to check.",
     "prior_action": "Escalated to Security (auto-flagged)"},
    {"id": "REQ-09", "employee": "Rohit Desai", "email": "rohit.desai@veridiancorp.example",
     "date": "Wed 23 Sep", "text": "My mailbox is full and I can't send emails.",
     "prior_action": "Not started"},
    {"id": "REQ-10", "employee": "Kavya Pillai", "email": "kavya.pillai@veridiancorp.example",
     "date": "Wed 23 Sep", "text": "Can someone give me admin access to the finance reporting server? Need it urgently for month-end.",
     "prior_action": "Not started"},
    {"id": "REQ-11", "employee": "Nikhil Bansal", "email": "nikhil.bansal@veridiancorp.example",
     "date": "Thu 24 Sep", "text": "New contractor joining my team next week, they'll need VPN access.",
     "prior_action": "Not started"},
    {"id": "REQ-12", "employee": "Sneha Kulkarni", "email": "sneha.kulkarni@veridiancorp.example",
     "date": "Thu 24 Sep", "text": "I can't log into the expense tool, keeps saying invalid credentials.",
     "prior_action": "Waiting on employee response (asked for a screenshot, no reply yet)"},
    {"id": "REQ-13", "employee": "Aman Gupta", "email": "aman.gupta@veridiancorp.example",
     "date": "Thu 24 Sep", "text": "Laptop screen is flickering on and off, had it 2 years, might just need a fix not a replacement.",
     "prior_action": "Not started"},
    {"id": "REQ-14", "employee": "Tanya Chopra", "email": "tanya.chopra@veridiancorp.example",
     "date": "Fri 25 Sep", "text": "Requesting approval to install a browser extension for productivity tracking.",
     "prior_action": "Not started"},
    {"id": "REQ-15", "employee": "Rahul Menon", "email": "rahul.menon@veridiancorp.example",
     "date": "Fri 25 Sep", "text": "hey can you help, its not working",
     "prior_action": "Not started"},
]

TICKET_QUEUE = [
    {"id": "TK-1042", "employee": "R. Verma", "issue": "VPN credential expired", "status": "Resolved (closed)"},
    {"id": "TK-1043", "employee": "S. Iyer", "issue": "Laptop replacement (3.2 yrs old)", "status": "Approved - pending fulfillment (active)"},
    {"id": "TK-1044", "employee": "A. Khan", "issue": "Non-catalog software request", "status": "Pending Security review (active)"},
    {"id": "TK-1045", "employee": "P. Joshi", "issue": "Mailbox quota increase", "status": "Approved at 35GB (closed)"},
    {"id": "TK-1046", "employee": "M. Das", "issue": "Printer paper jam, floor 2", "status": "Resolved (closed)"},
    {"id": "TK-1047", "employee": "K. Singh", "issue": "Home office equipment request", "status": "Pending Finance (active)"},
    {"id": "TK-1048", "employee": "T. Rao", "issue": "Phishing email reported", "status": "Escalated to Security - under investigation (active)"},
    {"id": "TK-1049", "employee": "V. Nambiar", "issue": "Password reset", "status": "Resolved (closed)"},
    {"id": "TK-1050", "employee": "J. Fernandes", "issue": "Admin access request", "status": "Rejected - no business justification provided (closed)"},
    {"id": "TK-1051", "employee": "L. Menon", "issue": "Guest Wi-Fi issued", "status": "Resolved (closed)"},
]

NEXT_TICKET_NUMBER = 1052
