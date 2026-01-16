import random
from mesa import Agent


class SpeculatorAgent(Agent):
    """
    Ticket scalper: buys scarce primary tickets early, relists them at a premium.
    """

    def __init__(self, unique_id, model, blockchain_interface, target_profit_margin=2.0):
        super().__init__(unique_id, model)
        self.blockchain_interface = blockchain_interface
        self.holdings = {}  # nft_id -> info
        self.target_profit_margin = target_profit_margin
        self.max_inventory = 10

    def step(self):
        # Intermittent activity to keep secondary market alive throughout the day
        if random.random() < 0.3:
            self._scalp_tickets()

        # Clean up stale inventory before listing
        self._manage_inventory()

        # List any holdings for resale
        self._list_holdings()

    def _scalp_tickets(self):
        # Fetch all available segments/offers
        segments = self.blockchain_interface.get_all_available_segments()
        current_step = self.model.current_step
        target_window_start = current_step + 5
        target_window_end = current_step + 60

        current_inventory = sum(1 for info in self.holdings.values()
                                if info.get('status') in ['held', 'listed'])
        if current_inventory >= self.max_inventory:
            return

        has_stale_inventory = any(
            (current_step - info.get('listed_at', current_step) > 10)
            for info in self.holdings.values()
            if info.get('status') == 'listed'
        )
        if has_stale_inventory:
            return

        target_offers = [
            s for s in segments
            if s.get('type') in ['offer', 'segment']  # PT broadcasts as segment
            and s.get('mode') in ['bus', 'train']
            and s.get('status') == 'available'
            and target_window_start <= s.get('depart_time', 0) <= target_window_end
        ]

        for offer in target_offers:
            depart_time = offer.get('depart_time', offer.get('start_time', 0))
            # Lower probability per step; continuous scanning keeps activity alive
            if random.random() < 0.2:
                est_duration = offer.get('estimated_time') or offer.get('duration')
                success, nft_id = self.blockchain_interface.mint_and_buy(
                    offer['offer_id'],
                    self.unique_id,
                    start_time=depart_time,
                    duration=est_duration
                )
                if success:
                    self.holdings[nft_id] = {
                        'original_price': offer.get('price', 0),
                        'status': 'held',
                        'acquired_at': current_step
                    }
                    self.model.logger.info(f"💰 Speculator {self.unique_id} scalped {nft_id} at {offer.get('price',0):.2f}")
                    # Log to central speculator ledger
                    if hasattr(self.model, "log_speculator_action"):
                        self.model.log_speculator_action(
                            self.unique_id, "scalp", nft_id, offer.get('price', 0), self.model.current_step
                        )

    def _manage_inventory(self):
        """Dump stale or expired holdings to free inventory."""
        current = self.model.current_step
        for nft_id, info in list(self.holdings.items()):
            acquired_at = info.get('acquired_at', current)
            # If held/listed more than 20 ticks without sale, dump it
            if current - acquired_at > 20:
                self.model.logger.info(f"🗑️ Speculator {self.unique_id} dumping stale ticket {nft_id}")
                # Remove from inventory; optional: could relist at fire sale
                del self.holdings[nft_id]

    def _list_holdings(self):
        for nft_id, info in list(self.holdings.items()):
            status = info.get('status')

            # If listed and stale, consider panic selling
            if status == 'listed':
                current = self.model.current_step
                listed_at = info.get('listed_at', current)
                if current - listed_at > 5:
                    old_price = info.get('listing_price', info.get('original_price', 1.0))
                    new_price = old_price * 0.8
                    if new_price > info.get('original_price', 0.1):
                        if self.blockchain_interface.list_nft_for_sale(nft_id, new_price):
                            info['listing_price'] = new_price
                            info['listed_at'] = current
                            self.model.logger.info(f"📉 Speculator {self.unique_id} CUT PRICE for {nft_id}: {old_price:.2f} -> {new_price:.2f}")
                    continue

            if status != 'held':
                continue

            # Peak-aware listing strategy
            current = self.model.current_step
            is_peak_hours = (30 <= current <= 90)

            should_list = False
            if is_peak_hours:
                should_list = random.random() < 0.3
            else:
                should_list = random.random() < 0.05

            if should_list:
                original_price = info.get('original_price', 1.0)
                margin_base = 3.0 if is_peak_hours else 1.5
                margin = margin_base * random.uniform(0.8, 1.5)
                resale_price = original_price * margin
                time_params = {
                    'initial_price': resale_price,
                    'final_price': original_price * 1.2,
                    'decay_duration': 20
                }

                success = self.blockchain_interface.list_nft_for_sale(nft_id, resale_price, time_params)
                if success:
                    info['status'] = 'listed'
                    info['listed_at'] = current
                    info['listing_price'] = resale_price
                    self.model.logger.info(f"📈 Speculator {self.unique_id} listed {nft_id} at {resale_price:.2f}")
                    if hasattr(self.model, "log_speculator_action"):
                        self.model.log_speculator_action(
                            self.unique_id, "list", nft_id, resale_price, self.model.current_step
                        )
