from flask import Flask, jsonify, request
import os

app = Flask(__name__)

error_code = os.environ.get("ERROR_CODE")


@app.route("/split-payments/compute", methods=["POST"])
def post_new_cafe():
    ID = request.form.get('ID')
    Amount = float(request.form.get('Amount'))
    Currency = request.form.get('Currency')
    CustomerEmail = request.form.get('CustomerEmail')
    first_info = request.form.get('SplitInfo')
    info = first_info.replace("    ", "")
    SplitInfo = list(eval(info))

    no_of_split_entities = len(SplitInfo)
    flat_values = []
    percentage_values = []
    ratio_values = []
    SplitBreakdown = []
    balance = Amount
    ratio_sum = 0
    if 1 <= no_of_split_entities <= 20:
        for info in SplitInfo:
            if info["SplitType"] == "FLAT":
                flat_values.append({info["SplitEntityId"]: int(info["SplitValue"])})
            elif info["SplitType"] == "PERCENTAGE":
                percentage_values.append({info["SplitEntityId"]: int(info["SplitValue"])})
            elif info["SplitType"] == "RATIO":
                ratio_values.append({info["SplitEntityId"]: int(info["SplitValue"])})
                ratio_sum += info["SplitValue"]
            else:
                return jsonify(response={"Error": f"{info['SplitType']} is an invalid SplitType"})

        for item in flat_values:
            for key, value in item.items():
                split = value
                balance = balance - split
                SplitBreakdown.append({
                    "SplitEntityId": key,
                    "Amount": split
                })

        for item in percentage_values:
            for key, value in item.items():
                split = (value/100) * balance
                balance = balance - split
                SplitBreakdown.append({
                    "SplitEntityId": key,
                    "Amount": split
                })

        RatioBalance = balance
        for item in ratio_values:
            for key, value in item.items():
                split = (value/ratio_sum) * RatioBalance
                balance = balance - split
                SplitBreakdown.append({
                    "SplitEntityId": key,
                    "Amount": split
                })

        FinalBalance = balance
        amounts = [item["Amount"] for item in SplitBreakdown]
        if FinalBalance < 0 or max(amounts) > Amount or min(amounts) < 0 or sum(amounts) > Amount:
            return jsonify(response={"Error": "Bad Request"}), error_code
        else:
            return jsonify({
                "ID": ID,
                "Balance": FinalBalance,
                "SplitBreakdown": SplitBreakdown
            })
    elif no_of_split_entities < 1:
        return jsonify(response={"Error": "There was no Split Info Added"}), 400
    else:
        return jsonify(response={"Error": "You exceeded the max number of 20 SplitInfo entries."}), 400


if __name__ == '__main__':
    app.run(debug=True)
