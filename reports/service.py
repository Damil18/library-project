"""Reports service."""
class ReportService:
    def __init__(self, loan_repo):
        self.loan_repo = loan_repo

    def loan_stats(self, start, end):
        loans = self.loan_repo.get_all()
        filtered = [l for l in loans if start <= l.issued_at < end]
        return {
            "from": start, "to": end, "total": len(filtered),
            "active": sum(1 for l in filtered if l.status == "active"),
            "returned": sum(1 for l in filtered if l.status == "returned"),
        }
