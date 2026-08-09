package domain

import "errors"

var (
	ErrInvalidTransition = errors.New("invalid state transition")
	ErrCancelledPayment  = errors.New("cancelled payment must be restored before it can be paid")
)
