package domain

import (
	"errors"
	"testing"
	"time"
)

func TestPaymentCannotBePaidAfterCancellationWithoutRestore(t *testing.T) {
	payment := PaymentObligation{Status: PaymentPending}
	now := time.Date(2026, 8, 9, 12, 0, 0, 0, time.UTC)
	if err := payment.ChangeStatus(PaymentCancelled, now); err != nil {
		t.Fatalf("cancel payment: %v", err)
	}
	if err := payment.ChangeStatus(PaymentPaid, now); !errors.Is(err, ErrCancelledPayment) {
		t.Fatalf("expected cancelled payment error, got %v", err)
	}
	if err := payment.Restore(now); err != nil {
		t.Fatalf("restore payment: %v", err)
	}
	if err := payment.ChangeStatus(PaymentPaid, now); err != nil {
		t.Fatalf("pay restored payment: %v", err)
	}
}

func TestMaintenanceTransitionIsAuditableAndResolvedIsTerminal(t *testing.T) {
	request := MaintenanceRequest{ID: "request-1", Status: MaintenanceSubmitted}
	now := time.Date(2026, 8, 9, 12, 0, 0, 0, time.UTC)
	transition, err := request.ChangeStatus(MaintenanceUnderReview, "manager-1", "received", now)
	if err != nil {
		t.Fatalf("change status: %v", err)
	}
	if transition.From != MaintenanceSubmitted || transition.To != MaintenanceUnderReview || transition.ChangedBy != "manager-1" {
		t.Fatalf("unexpected transition: %+v", transition)
	}
	if _, err := request.ChangeStatus(MaintenanceInProgress, "manager-1", "skip", now); !errors.Is(err, ErrInvalidTransition) {
		t.Fatalf("expected invalid skipped transition, got %v", err)
	}
	if _, err := request.ChangeStatus(MaintenancePlanned, "manager-1", "scheduled", now); err != nil {
		t.Fatalf("plan request: %v", err)
	}
	if _, err := request.ChangeStatus(MaintenanceInProgress, "manager-1", "started", now); err != nil {
		t.Fatalf("start request: %v", err)
	}
	if _, err := request.ChangeStatus(MaintenanceResolved, "manager-1", "fixed", now); err != nil {
		t.Fatalf("resolve request: %v", err)
	}
	if request.ResolvedAt == nil || !request.ResolvedAt.Equal(now) {
		t.Fatalf("expected resolved timestamp, got %v", request.ResolvedAt)
	}
	if _, err := request.ChangeStatus(MaintenanceInProgress, "manager-1", "reopen", now); !errors.Is(err, ErrInvalidTransition) {
		t.Fatalf("expected terminal request error, got %v", err)
	}
}

func TestAnnouncementAndMembershipAreTimeScoped(t *testing.T) {
	start := time.Date(2026, 8, 9, 12, 0, 0, 0, time.UTC)
	expires := start.Add(time.Hour)
	announcement := Announcement{Status: AnnouncementPublished, PublishedAt: &start, ExpiresAt: &expires}
	if !announcement.ActiveAt(start) || announcement.ActiveAt(expires) {
		t.Fatal("announcement should be active only within its publication window")
	}
	until := start.Add(time.Hour)
	membership := Membership{ActiveFrom: start, ActiveUntil: &until}
	if !membership.ActiveAt(start) || membership.ActiveAt(until) {
		t.Fatal("membership should be active only within its membership window")
	}
}
