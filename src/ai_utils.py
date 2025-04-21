import os
import ollama
import pandas as pd


def _build_portfolio_summary(df: pd.DataFrame) -> str:
    """
    Transforme le DataFrame en résumé JSON-friendly pour l’IA.
    Ne garde que symbol, balance et total_value.
    """
    records = df[['symbol', 'balance', 'total_value']].fillna(0).to_dict(orient='records')
    return str(records)

def ask_portfolio_question(df: pd.DataFrame, question: str, model: str = "llama2") -> str:
    summary = _build_portfolio_summary(df)
    prompt = (
        "You are a financial assistant. \n"
        "Here is the portfolio data:\n"
        f"{summary}\n"
        f"Question: {question}\n"
        "Please answer clearly and concisely.\n"
    )
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a portfolio management expert."},
            {"role": "user", "content": prompt}
        ],
    )
    return resp['message']['content'].strip()

def suggest_optimized_allocation(df: pd.DataFrame, model: str = "llama2") -> str:
    summary = _build_portfolio_summary(df)
    prompt = (
        "You are an experienced portfolio manager.\n"
        "Based on these positions:\n"
        f"{summary}\n"
        "Propose an optimized allocation (in percentages) for each symbol,\n"
        "balancing risk and return."
    )
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a finance and portfolio optimization expert."},
            {"role": "user", "content": prompt}
        ],
    )
    return resp['message']['content'].strip()
