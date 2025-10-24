from src.services.matching_engine import MatchingEngineService

def test_lob_basic_flow():
    engine = MatchingEngineService()

    # Add sample buy/sell orders
    engine.submit_order(1, 100.0, 10)
    engine.submit_order(-1, 99.5, 5)

    print(engine.get_top_of_book())

if __name__ == "__main__":
    test_lob_basic_flow()