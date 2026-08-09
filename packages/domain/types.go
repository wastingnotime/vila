package domain

import "time"

type Role string

const (
	RoleResident        Role = "resident"
	RoleBuildingManager Role = "building_manager"
)

type CondominiumStatus string

const (
	CondominiumActive   CondominiumStatus = "active"
	CondominiumInactive CondominiumStatus = "inactive"
)

type UnitStatus string

const (
	UnitActive   UnitStatus = "active"
	UnitInactive UnitStatus = "inactive"
)

type AnnouncementPriority string

const (
	PriorityNormal AnnouncementPriority = "normal"
	PriorityHigh   AnnouncementPriority = "high"
)

type AnnouncementStatus string

const (
	AnnouncementDraft     AnnouncementStatus = "draft"
	AnnouncementPublished AnnouncementStatus = "published"
	AnnouncementExpired   AnnouncementStatus = "expired"
)

type PaymentStatus string

const (
	PaymentPending   PaymentStatus = "pending"
	PaymentPaid      PaymentStatus = "paid"
	PaymentOverdue   PaymentStatus = "overdue"
	PaymentCancelled PaymentStatus = "cancelled"
)

type MaintenanceStatus string

const (
	MaintenanceSubmitted   MaintenanceStatus = "submitted"
	MaintenanceUnderReview MaintenanceStatus = "under_review"
	MaintenancePlanned     MaintenanceStatus = "planned"
	MaintenanceInProgress  MaintenanceStatus = "in_progress"
	MaintenanceResolved    MaintenanceStatus = "resolved"
	MaintenanceRejected    MaintenanceStatus = "rejected"
)

type DeliveryStatus string

const (
	DeliveryWaiting   DeliveryStatus = "waiting"
	DeliveryCollected DeliveryStatus = "collected"
)

type Condominium struct {
	ID        string
	Name      string
	Status    CondominiumStatus
	CreatedAt time.Time
}

type Unit struct {
	ID            string
	CondominiumID string
	Label         string
	Status        UnitStatus
}

type Membership struct {
	ID            string
	CondominiumID string
	UnitID        string
	UserID        string
	Role          Role
	ActiveFrom    time.Time
	ActiveUntil   *time.Time
}

func (m Membership) ActiveAt(at time.Time) bool {
	if at.Before(m.ActiveFrom) {
		return false
	}
	return m.ActiveUntil == nil || at.Before(*m.ActiveUntil)
}

type Announcement struct {
	ID            string
	CondominiumID string
	Title         string
	Body          string
	Priority      AnnouncementPriority
	PublishedAt   *time.Time
	ExpiresAt     *time.Time
	Status        AnnouncementStatus
}

func (a Announcement) ActiveAt(at time.Time) bool {
	if a.Status != AnnouncementPublished || a.PublishedAt == nil || at.Before(*a.PublishedAt) {
		return false
	}
	return a.ExpiresAt == nil || at.Before(*a.ExpiresAt)
}

type PaymentObligation struct {
	ID               string
	CondominiumID    string
	UnitID           string
	Description      string
	AmountInCents    int64
	DueDate          time.Time
	PaymentReference string
	ExternalURL      string
	PixPayload       string
	Status           PaymentStatus
	PaidAt           *time.Time
}

func (p *PaymentObligation) ChangeStatus(next PaymentStatus, at time.Time) error {
	if p.Status == PaymentCancelled && next == PaymentPaid {
		return ErrCancelledPayment
	}
	if !validPaymentTransition(p.Status, next) {
		return ErrInvalidTransition
	}
	p.Status = next
	if next == PaymentPaid {
		when := at
		p.PaidAt = &when
	} else {
		p.PaidAt = nil
	}
	return nil
}

func (p *PaymentObligation) Restore(at time.Time) error {
	if p.Status != PaymentCancelled {
		return ErrInvalidTransition
	}
	p.Status = PaymentPending
	p.PaidAt = nil
	return nil
}

func validPaymentTransition(from, to PaymentStatus) bool {
	if from == to {
		return false
	}
	switch from {
	case PaymentPending:
		return to == PaymentPaid || to == PaymentOverdue || to == PaymentCancelled
	case PaymentOverdue:
		return to == PaymentPaid || to == PaymentCancelled
	default:
		return false
	}
}

type MaintenanceRequest struct {
	ID            string
	CondominiumID string
	UnitID        string
	OpenedBy      string
	Category      string
	Description   string
	Status        MaintenanceStatus
	CreatedAt     time.Time
	ResolvedAt    *time.Time
}

type MaintenanceTransition struct {
	RequestID string
	From      MaintenanceStatus
	To        MaintenanceStatus
	ChangedBy string
	Note      string
	ChangedAt time.Time
}

func (r *MaintenanceRequest) ChangeStatus(next MaintenanceStatus, changedBy, note string, at time.Time) (MaintenanceTransition, error) {
	if !validMaintenanceTransition(r.Status, next) {
		return MaintenanceTransition{}, ErrInvalidTransition
	}
	transition := MaintenanceTransition{RequestID: r.ID, From: r.Status, To: next, ChangedBy: changedBy, Note: note, ChangedAt: at}
	r.Status = next
	if next == MaintenanceResolved {
		when := at
		r.ResolvedAt = &when
	}
	return transition, nil
}

func validMaintenanceTransition(from, to MaintenanceStatus) bool {
	if from == to || from == MaintenanceResolved || from == MaintenanceRejected {
		return false
	}
	switch from {
	case MaintenanceSubmitted:
		return to == MaintenanceUnderReview || to == MaintenanceRejected
	case MaintenanceUnderReview:
		return to == MaintenancePlanned || to == MaintenanceRejected
	case MaintenancePlanned:
		return to == MaintenanceInProgress || to == MaintenanceRejected
	case MaintenanceInProgress:
		return to == MaintenanceResolved
	default:
		return false
	}
}

type Delivery struct {
	ID            string
	CondominiumID string
	UnitID        string
	Description   string
	ReceivedAt    time.Time
	CollectedAt   *time.Time
	Status        DeliveryStatus
}

func (d *Delivery) Collect(at time.Time) error {
	if d.Status != DeliveryWaiting {
		return ErrInvalidTransition
	}
	d.Status = DeliveryCollected
	d.CollectedAt = &at
	return nil
}
