"use client";

import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  fetchUsers, 
  formatDate, 
  getRoleColor,
  type User 
} from "@/lib/api";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const response = await fetchUsers(50, 0);
        setUsers(response.data);
        setTotalCount(response.count || 0);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch users");
      } finally {
        setLoading(false);
      }
    };

    loadUsers();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-text-secondary">Loading users...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-neon-red/10 border border-neon-red/30 rounded-lg p-4">
        <p className="text-neon-red">Error: {error}</p>
        <p className="text-sm text-neon-red/70 mt-1">
          Make sure the backend is running and you have admin access.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-text-primary font-display">Users</h1>
        <span className="text-sm text-text-tertiary">
          {totalCount} total user{totalCount !== 1 ? "s" : ""}
        </span>
      </div>

      <Card className="bg-bg-surface-2/50 border-border-default backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg text-text-primary">All Users</CardTitle>
        </CardHeader>
        <CardContent>
          {users.length === 0 ? (
            <p className="text-text-secondary text-center py-8">
              No users found. Run the seed script to create demo users.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Sessions</TableHead>
                  <TableHead>Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.email}</TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(
                          user.role
                        )}`}
                      >
                        {user.role}
                      </span>
                    </TableCell>
                    <TableCell>{user.session_count}</TableCell>
                    <TableCell className="text-text-tertiary text-sm">
                      {formatDate(user.created_at)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
