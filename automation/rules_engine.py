class AutomationRulesEngine:
    def __init__(self, db, alert_engine):
        self.db = db
        self.alert_engine = alert_engine

    def execute_rule_bed_capacity(self):
        return self.alert_engine.check_bed_capacity()

    def execute_rule_pharmacy_stock(self):
        return self.alert_engine.check_pharmacy_stock()

    def execute_rule_claim_aging(self):
        return self.alert_engine.check_claim_aging()

    def execute_rule_waiting_times(self):
        return self.alert_engine.check_waiting_times()

    def execute_rule_staff_coverage(self):
        return self.alert_engine.check_staff_coverage()

    def execute_rule_payment_aging(self):
        return self.alert_engine.check_payment_aging()

    def execute_rule_lab_delays(self):
        return self.alert_engine.check_lab_delays()
        
    def run_all_rules(self):
        return self.alert_engine.run_all_checks()
