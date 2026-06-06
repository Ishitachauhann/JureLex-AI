# bns_mapping.py
# Bidirectional mapping between Indian Penal Code (IPC) and Bharatiya Nyaya Sanhita (BNS)

# Format: IPC_SECTION: { bns_section, title, description }
IPC_TO_BNS = {
    "34": {
        "bns_section": "3(5)",
        "title": "Joint Liability (Common Intention)",
        "desc": "Acts done by several persons in furtherance of common intention."
    },
    "120A": {
        "bns_section": "61(1)",
        "title": "Definition of Criminal Conspiracy",
        "desc": "Agreement between two or more persons to commit an illegal act."
    },
    "120B": {
        "bns_section": "61(2)",
        "title": "Punishment for Criminal Conspiracy",
        "desc": "Punishment for participating in a criminal conspiracy."
    },
    "124A": {
        "bns_section": "152",
        "title": "Sedition / Act Endangering Sovereignty",
        "desc": "Acts exciting disaffection, secession, armed rebellion, or endangering the sovereignty, unity, and integrity of India."
    },
    "141": {
        "bns_section": "189(1)",
        "title": "Unlawful Assembly",
        "desc": "Assembly of five or more persons with a common unlawful object."
    },
    "143": {
        "bns_section": "189(2)",
        "title": "Punishment for Unlawful Assembly",
        "desc": "Punishment for being a member of an unlawful assembly."
    },
    "147": {
        "bns_section": "191(1)",
        "title": "Rioting",
        "desc": "Guilty of rioting when force or violence is used by an unlawful assembly."
    },
    "149": {
        "bns_section": "190",
        "title": "Every member of unlawful assembly guilty of offence",
        "desc": "Constructive joint liability for offences committed in prosecution of common object."
    },
    "299": {
        "bns_section": "100",
        "title": "Culpable Homicide",
        "desc": "Causing death by doing an act with the intention/knowledge of causing death."
    },
    "300": {
        "bns_section": "101",
        "title": "Murder",
        "desc": "Culpable homicide defined as murder with specific intent, bodily injury, or imminent danger."
    },
    "302": {
        "bns_section": "103(1)",
        "title": "Punishment for Murder",
        "desc": "Punishment of death or imprisonment for life, and liability to fine."
    },
    "304A": {
        "bns_section": "106(1)",
        "title": "Causing Death by Negligence",
        "desc": "Causing death of any person by doing any rash or negligent act not amounting to culpable homicide."
    },
    "304B": {
        "bns_section": "80",
        "title": "Dowry Death",
        "desc": "Death of a woman caused by burns, bodily injury, or occurring under abnormal circumstances within 7 years of marriage due to dowry harassment."
    },
    "307": {
        "bns_section": "109",
        "title": "Attempt to Murder",
        "desc": "Doing an act with such intention or knowledge that if it caused death, it would be murder."
    },
    "319": {
        "bns_section": "115(1)",
        "title": "Hurt",
        "desc": "Causing bodily pain, disease, or infirmity to any person."
    },
    "320": {
        "bns_section": "116",
        "title": "Grievous Hurt",
        "desc": "Specific severe kinds of hurt, including emasculation, permanent loss of sight/hearing, fracture, or 15 days of severe pain."
    },
    "323": {
        "bns_section": "115(2)",
        "title": "Punishment for Voluntarily Causing Hurt",
        "desc": "Punishment for voluntarily causing simple hurt."
    },
    "324": {
        "bns_section": "117(1)",
        "title": "Voluntarily Causing Hurt by Dangerous Weapons",
        "desc": "Voluntarily causing hurt by means of instruments for shooting, stabbing, or cutting."
    },
    "325": {
        "bns_section": "117(2)",
        "title": "Punishment for Voluntarily Causing Grievous Hurt",
        "desc": "Punishment for voluntarily causing grievous hurt."
    },
    "339": {
        "bns_section": "126(1)",
        "title": "Wrongful Restraint",
        "desc": "Voluntarily obstructing any person so as to prevent that person from proceeding in any direction."
    },
    "340": {
        "bns_section": "127(1)",
        "title": "Wrongful Confinement",
        "desc": "Wrongfully restraining any person in such a manner as to prevent that person from proceeding beyond certain circumscribing limits."
    },
    "341": {
        "bns_section": "126(2)",
        "title": "Punishment for Wrongful Restraint",
        "desc": "Punishment for wrongfully restraining a person."
    },
    "342": {
        "bns_section": "127(2)",
        "title": "Punishment for Wrongful Confinement",
        "desc": "Punishment for wrongfully confining a person."
    },
    "349": {
        "bns_section": "128",
        "title": "Force",
        "desc": "Causing motion, change of motion, or cessation of motion to another person."
    },
    "350": {
        "bns_section": "129",
        "title": "Criminal Force",
        "desc": "Intentionally using force to any person without that person's consent to commit an offence or cause injury, fear, or annoyance."
    },
    "351": {
        "bns_section": "130",
        "title": "Assault",
        "desc": "Making any gesture or preparation intending or knowing it will cause another to apprehend criminal force."
    },
    "354": {
        "bns_section": "74",
        "title": "Outraging Modesty of Woman",
        "desc": "Assault or criminal force to woman with intent to outrage her modesty."
    },
    "361": {
        "bns_section": "137",
        "title": "Kidnapping from guardianship",
        "desc": "Taking or enticing any minor or person of unsound mind out of the keeping of the lawful guardian."
    },
    "362": {
        "bns_section": "138",
        "title": "Abduction",
        "desc": "Compelling by force or inducing by deceitful means any person to go from any place."
    },
    "363": {
        "bns_section": "137(2)",
        "title": "Punishment for Kidnapping",
        "desc": "Punishment for kidnapping a person from India or from lawful guardianship."
    },
    "375": {
        "bns_section": "63",
        "title": "Rape (Definition)",
        "desc": "Definition of sexual intercourse under specific non-consensual circumstances."
    },
    "376": {
        "bns_section": "64",
        "title": "Punishment for Rape",
        "desc": "Imprisonment of not less than 10 years, which may extend to life imprisonment, and fine."
    },
    "378": {
        "bns_section": "303(1)",
        "title": "Theft",
        "desc": "Intending to take dishonestly any movable property out of the possession of any person without consent."
    },
    "379": {
        "bns_section": "303(2)",
        "title": "Punishment for Theft",
        "desc": "Punishment for committing theft, including community service for first-time offenders of small value."
    },
    "390": {
        "bns_section": "309(1)",
        "title": "Robbery",
        "desc": "Theft or extortion becomes robbery when causing death, hurt, or wrongful restraint in the commission."
    },
    "391": {
        "bns_section": "310(1)",
        "title": "Dacoity",
        "desc": "When five or more persons conjointly commit or attempt to commit robbery."
    },
    "395": {
        "bns_section": "310(2)",
        "title": "Punishment for Dacoity",
        "desc": "Punishment with imprisonment for life, or with rigorous imprisonment up to 10 years, and fine."
    },
    "405": {
        "bns_section": "316(1)",
        "title": "Criminal Breach of Trust (Definition)",
        "desc": "Dishonest misappropriation or conversion of property entrusted."
    },
    "406": {
        "bns_section": "316(2)",
        "title": "Punishment for Criminal Breach of Trust",
        "desc": "Punishment for committing criminal breach of trust."
    },
    "415": {
        "bns_section": "318(1)",
        "title": "Cheating",
        "desc": "Deceiving any person and fraudulently inducing delivery of property or consent to retain property."
    },
    "420": {
        "bns_section": "318(4)",
        "title": "Punishment for Cheating (with delivery of property)",
        "desc": "Cheating and dishonestly inducing delivery of property, punishable by up to 7 years."
    },
    "441": {
        "bns_section": "329(1)",
        "title": "Criminal Trespass",
        "desc": "Entering into or upon property in possession of another with intent to commit an offence."
    },
    "498A": {
        "bns_section": "85",
        "title": "Cruelty by Husband or Relatives",
        "desc": "Subjecting a married woman to cruelty by her husband or relatives of her husband."
    },
    "499": {
        "bns_section": "356(1)",
        "title": "Defamation (Definition)",
        "desc": "Making or publishing any imputation intending to harm the reputation of a person."
    },
    "500": {
        "bns_section": "356(2)",
        "title": "Punishment for Defamation",
        "desc": "Punishment with simple imprisonment, fine, or community service."
    },
    "503": {
        "bns_section": "351(1)",
        "title": "Criminal Intimidation",
        "desc": "Threatening another with injury to their person, reputation, or property to cause alarm."
    },
    "506": {
        "bns_section": "351(2)",
        "title": "Punishment for Criminal Intimidation",
        "desc": "Punishment for committing criminal intimidation."
    },
    "509": {
        "bns_section": "79",
        "title": "Insulting Modesty of Woman",
        "desc": "Word, gesture, or act intended to insult the modesty of a woman."
    }
}

# Reverse mapping for BNS to IPC
BNS_TO_IPC = {}
for ipc_sec, data in IPC_TO_BNS.items():
    bns_sec = data["bns_section"]
    BNS_TO_IPC[bns_sec] = {
        "ipc_section": ipc_sec,
        "title": data["title"],
        "desc": data["desc"]
    }

def lookup_ipc(ipc_section: str) -> dict:
    """Find BNS equivalent for a given IPC section."""
    clean_sec = ipc_section.strip().upper()
    return IPC_TO_BNS.get(clean_sec, None)

def lookup_bns(bns_section: str) -> dict:
    """Find IPC equivalent for a given BNS section."""
    clean_sec = bns_section.strip().upper()
    return BNS_TO_IPC.get(clean_sec, None)

def extract_sections_from_text(text: str) -> dict:
    """Scan query text for IPC or BNS sections and return transition mappings."""
    import re
    # Match "Section 302", "Sec 302", "Sec. 302", "Section 498A", "Section 3(5)"
    sec_regex = re.compile(r'\b(?:section|sec\.?)\s+(\d+(?:\(\d+\))?[A-Z]?)\b', re.IGNORECASE)
    matches = sec_regex.findall(text)
    
    transitions = []
    seen = set()
    
    for match in matches:
        if match in seen:
            continue
        seen.add(match)
        
        # Check if it's IPC
        ipc_info = lookup_ipc(match)
        if ipc_info:
            transitions.append({
                "type": "IPC_TO_BNS",
                "source": match,
                "target": ipc_info["bns_section"],
                "title": ipc_info["title"],
                "desc": ipc_info["desc"]
            })
            continue
            
        # Check if it's BNS
        bns_info = lookup_bns(match)
        if bns_info:
            transitions.append({
                "type": "BNS_TO_IPC",
                "source": match,
                "target": bns_info["ipc_section"],
                "title": bns_info["title"],
                "desc": bns_info["desc"]
            })
            
    return transitions
