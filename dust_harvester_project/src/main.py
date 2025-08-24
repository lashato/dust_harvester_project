import asyncio
from src.config import settings
from src.utils.gas import is_profitable
from src.incentives.amm_skim import AmmSkim

async def run():
    """Main harvester execution function"""
    print("Starting Onchain Dust Harvester...")
    print(f"Mode: {'DRY RUN' if settings.DRY_RUN else 'LIVE'}")
    print(f"Chain ID: {settings.CHAIN_ID}")
    print(f"Max pairs to check: {settings.MAX_PAIRS}")
    
    strat = AmmSkim()
    candidates = await strat.discover_candidates()
    print(f"Проверено — кандидатов всего: {len(candidates)}")
    
    # Save candidates to file
    with open('candidates.txt', 'w') as f:
        for c in candidates:
            f.write(f"{c[0]} {c[1]} {c[2]}\n")
    
    # candidates are (pair, token, surplus)
    executed_count = 0
    for c in candidates:
        if await is_profitable(c):
            await strat.execute_candidate(c)
            executed_count += 1
        else:
            # для больших списков можно логировать редкое событие
            pass
    
    print(f"Executed {executed_count} profitable candidates")
    return executed_count

if __name__ == "__main__":
    asyncio.run(run())
