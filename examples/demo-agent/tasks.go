// DEMO DATA: a made-up Go helper that turns action items into Google Tasks.
package demo

import (
	"context"

	"google.golang.org/api/option"
	tasks "google.golang.org/api/tasks/v1"
)

func AddItems(ctx context.Context, opts []option.ClientOption, listID string, items []string) error {
	srv, err := tasks.NewService(ctx, opts...)
	if err != nil {
		return err
	}
	for _, it := range items {
		if _, err := srv.Tasks.Insert(listID, &tasks.Task{Title: it}).Do(); err != nil {
			return err
		}
	}
	_, err = srv.Tasks.Move(listID, "TASK_ID").Do()
	return err
}
