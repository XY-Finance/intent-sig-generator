import os

import openai
import pandas as pd


def get_address_transactions(address: str) -> pd.DataFrame:
    df = pd.read_csv("ml/data/raw/collected_transactions.csv")
    df = df.drop(columns=["input", "blockHash", "hash"])

    return df[(df["address"] == address)]


def summarize_transactions_with_llm(address: str, tx_df: pd.DataFrame):
    limited_tx = tx_df.head(60)
    tx_text = limited_tx.to_string(index=False)
    prompt = f"""
    我有一個區塊鏈地址：{address}
    以下是它最近的交易紀錄：
    {tx_text}

    請幫我總結該地址的活動特性或可疑行為，例如：
    - 是否活躍？
    - 和哪一個地址互動最頻繁，可以的話查詢該地址是什麼項目？
    - 扣除approve，最頻繁的行為(functionName)是什麼？
    - 有沒有重複的收款/轉帳對象？
    - 平均間隔多久交易一次？
    - 有無和誰進行大額交易/轉帳？

    請用條列式給出 insight。
    """
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM API error: {e}"


if __name__ == "__main__":
    target_address = "0x40c5df45ff0f0782bff92149efb3361070353666"
    txs = get_address_transactions(target_address)

    if len(txs) == 0:
        print("找不到該地址的交易紀錄。")
    else:
        print("正在分析交易紀錄...")
        summary = summarize_transactions_with_llm(target_address, txs)
        print("\n💡 Insight 結果：\n")
        print(summary)
