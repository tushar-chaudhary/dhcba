from collections import defaultdict
import json


def getHistory():
    imgs = ["http://delhihighcourt.nic.in/assetsweb/images/history_big.jpg",
            "http://delhihighcourt.nic.in/assetsweb/images/history_big1.jpg"]

    all_history = {}
    all_history["imgs"] = imgs

    all_history["text"] = [
        """The High Court of Delhi was established on 31st October, 1966.Initially, the High Court of Judicature at Lahore, which was established by a Letters Patent dated 21st March, 1919, exercised jurisdiction over the then provinces of the Punjab and Delhi. This position continued till the Indian Independence Act, 1947 when the dominions of India and Pakistan were created.""",
        """The High Courts (Punjab) Order, 1947 established a new High Court for the territory of what was then called the East Punjab with effect from 15th August, 1947. The India (Adaptation of Existing Indian Laws) Order, 1947 provided that any reference in an existing Indian law to the High Court of Judicature at Lahore, be replaced by a reference to the High Court of East Punjab. The High Court of East Punjab started functioning from Shimla in a building called "Peterhoff". This building burnt down in January, 1981. When the Secretariat of the Punjab Government shifted to Chandigarh in 1954-55, the High Court also shifted to Chandigarh. The High Court of Punjab, as it is later came to be called, exercised jurisdiction over Delhi through a Circuit Bench which dealt with the cases pertaining to the Union Territory of Delhi and the Delhi Administration.""",
        """In view of the importance of Delhi, its population and other considerations, Parliament thought it necessary to establish a new High Court of Delhi. This was achieved by enacting the Delhi High Court Act, 1966 on 5th September, 1966. The High Court of Delhi initially exercised jurisdiction not only over the Union Territory of Delhi, but also Himachal Pradesh. The High Court of Delhi had a Himachal Pradesh Bench at Shimla in a building called Ravenswood. The High Court of Delhi continued to exercise jurisdiction over Himachal Pradesh until the State of Himachal Pradesh Act, 1970 was enforced on 25th January, 1971. The High Court of Delhi was established with four Judges. They were Chief Justice K.S.Hegde, Justice I.D.Dua, Justice H.R.Khanna and Justice S.K.Kapur. The sanctioned strength of Judges of this High Court increased from time to time. Presently, the sanctioned strength of Judges of the High Court of Delhi is 29 permanent Judges and 19 Additional Judges."""]

    history_result = json.dumps({"history": all_history})

    return history_result
