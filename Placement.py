import sqlite3

class Database:
    def __init__(self, db_name="candidates.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY,
                name TEXT,
                gpa REAL,
                experience INTEGER,
                skills TEXT,
                coding_marks REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_slots (
                time TEXT PRIMARY KEY,
                candidate_id INTEGER,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        """)
        self.connection.commit()

    def add_candidate(self, candidate):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO candidates (id, name, gpa, experience, skills, coding_marks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (candidate.id, candidate.name, candidate.gpa, candidate.experience, ",".join(candidate.skills), candidate.coding_marks))
        self.connection.commit()

    def delete_candidate(self, candidate_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        self.connection.commit()

    def get_candidate_by_id(self, candidate_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        return cursor.fetchone()

    def get_candidates_by_gpa(self, gpa):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM candidates WHERE gpa = ?", (gpa,))
        return cursor.fetchall()

class Candidate:
    def __init__(self, id, name, gpa, experience, skills, coding_marks):
        self.id = id
        self.name = name
        self.gpa = gpa
        self.experience = experience
        self.skills = skills
        self.coding_marks = coding_marks

class ListNode:
    def __init__(self, candidate):
        self.candidate = candidate
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, candidate):
        new_node = ListNode(candidate)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node

    def __iter__(self):
        current = self.head
        while current:
            yield current.candidate
            current = current.next

class BSTNode:
    def __init__(self, gpa):
        self.gpa = gpa
        self.linked_list = LinkedList()
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, candidate):
        if self.root is None:
            self.root = BSTNode(candidate.gpa)
            self.root.linked_list.insert(candidate)
        else:
            self._insert(self.root, candidate)

    def _insert(self, node, candidate):
        if candidate.gpa < node.gpa:
            if node.left is None:
                node.left = BSTNode(candidate.gpa)
                node.left.linked_list.insert(candidate)
            else:
                self._insert(node.left, candidate)
        elif candidate.gpa > node.gpa:
            if node.right is None:
                node.right = BSTNode(candidate.gpa)
                node.right.linked_list.insert(candidate)
            else:
                self._insert(node.right, candidate)
        else:
            node.linked_list.insert(candidate)

    def search(self, gpa):
        return self._search(self.root, gpa)

    def _search(self, node, gpa):
        if node is None or node.gpa == gpa:
            return node
        if gpa < node.gpa:
            return self._search(node.left, gpa)
        return self._search(node.right, gpa)

    def in_order_traversal(self):
        nodes = []
        self._in_order_traversal(self.root, nodes)
        return nodes

    def _in_order_traversal(self, node, nodes):
        if node:
            self._in_order_traversal(node.left, nodes)
            nodes.append(node)
            self._in_order_traversal(node.right, nodes)

class InterviewSlot:
    def __init__(self, time, candidate=None):
        self.time = time
        self.candidate = candidate

class Scheduler:
    def __init__(self):
        self.slots = []

    def add_slot(self, time):
        self.slots.append(InterviewSlot(time))

    def schedule_candidate(self, time, candidate):
        for slot in self.slots:
            if slot.time == time and slot.candidate is None:
                slot.candidate = candidate
                return True
        return False

    def get_schedule(self):
        return [(slot.time, slot.candidate.name if slot.candidate else "Free") for slot in self.slots]

class CandidateSelectionSystem:
    def __init__(self):
        self.bst = BST()
        self.scheduler = Scheduler()
        self.db = Database()
        self.hash_table = {}
        self._load_candidates_from_db()  

    def _load_candidates_from_db(self):
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT * FROM candidates")
        for row in cursor.fetchall():
            id, name, gpa, experience, skills, coding_marks = row
            skills_list = skills.split(",") 
            candidate = Candidate(id, name, gpa, experience, skills_list, coding_marks)
            self.bst.insert(candidate)
            self.hash_table[candidate.id] = candidate

    def add_candidate(self, candidate):
        self.bst.insert(candidate)
        self.hash_table[candidate.id] = candidate
        self.db.add_candidate(candidate)

    def delete_candidate(self, candidate_id):
        if candidate_id in self.hash_table:
            del self.hash_table[candidate_id]
            self.db.delete_candidate(candidate_id)
            print(f"Candidate with ID {candidate_id} deleted successfully.")
        else:
            print("Candidate not found.")

    def search_candidate_by_id(self, candidate_id):
        return self.hash_table.get(candidate_id, None)

    def search_candidate_by_gpa(self, gpa):
        node = self.bst.search(gpa)
        if node:
            return list(node.linked_list)
        return []

    def sort_candidates_by_gpa(self):
        nodes = self.bst.in_order_traversal()
        sorted_candidates = []
        for node in nodes:
            for candidate in node.linked_list:
                sorted_candidates.append(candidate)
        return sorted_candidates

    def shortlist_candidates(self, min_gpa, required_skills, min_experience, min_coding_marks):
        shortlisted = []
        nodes = self.bst.in_order_traversal()
        for node in nodes:
            if node.gpa >= min_gpa:
                for candidate in node.linked_list:
                    if (candidate.experience >= min_experience and
                        candidate.coding_marks >= min_coding_marks and
                        all(skill in candidate.skills for skill in required_skills)):
                        shortlisted.append(candidate)
        return shortlisted

    def filter_candidates_by_coding_marks(self, min_marks):
        return [candidate for candidate in self.hash_table.values() if candidate.coding_marks >= min_marks]

    def schedule_candidate(self, time, candidate_id):
        candidate = self.search_candidate_by_id(candidate_id)
        if candidate:
            self.scheduler.add_slot(time)
            return self.scheduler.schedule_candidate(time, candidate)
        return False

    def get_schedule(self):
        return self.scheduler.get_schedule()

    def generate_report(self):
        report = {
            "total_candidates": len(self.hash_table),
            "shortlisted_candidates": len(self.shortlist_candidates(3.5, ['Python', 'Data Structures'], 2, 75)),
            "all_candidates": [(candidate.id, candidate.name, candidate.gpa, candidate.experience, candidate.skills, candidate.coding_marks) for candidate in self.hash_table.values()]
        }
        return report

def main():
    system = CandidateSelectionSystem()

    while True:
        print("\nCandidate Selection System Menu")
        print("1. Add Candidate")
        print("2. Search Candidate by ID")
        print("3. Search Candidate by GPA")
        print("4. Sort Candidates by GPA")
        print("5. Shortlist Candidates")
        print("6. Filter Candidates by Coding Test Marks")
        print("7. Schedule Interview")
        print("8. View Schedule")
        print("9. Generate All Candidate Details")
        print("10. Delete Candidate") 
        print("11. Exit")  

        choice = input("Enter your choice: ")

        if choice == "1":
            id = int(input("Enter ID: "))
            name = input("Enter Name: ")
            gpa = float(input("Enter GPA: "))
            experience = int(input("Enter Experience (in years): "))
            skills = input("Enter Skills (comma separated): ").split(",")
            coding_marks = float(input("Enter marks in coding test: "))
            candidate = Candidate(id, name, gpa, experience, skills, coding_marks)
            system.add_candidate(candidate)
            print(f"Candidate {name} added successfully.")

        elif choice == "2":
            id = int(input("Enter ID: "))
            candidate = system.search_candidate_by_id(id)
            if candidate:
                print(f"ID: {candidate.id}, Name: {candidate.name}, GPA: {candidate.gpa}, "
                      f"Experience: {candidate.experience}, Skills: {', '.join(candidate.skills)}, "
                      f"Coding Marks: {candidate.coding_marks}")
            else:
                print("Candidate not found.")

        elif choice == "3":
            gpa = float(input("Enter GPA: "))
            candidates = system.search_candidate_by_gpa(gpa)
            if candidates:
                for candidate in candidates:
                    print(f"ID: {candidate.id}, Name: {candidate.name}, GPA: {candidate.gpa}, "
                          f"Experience: {candidate.experience}, Skills: {', '.join(candidate.skills)}, "
                          f"Coding Marks: {candidate.coding_marks}")
            else:
                print("No candidates found with the specified GPA.")

        elif choice == "4":
            candidates = system.sort_candidates_by_gpa()
            print("Candidates sorted by GPA:")
            for candidate in candidates:
                print(f"GPA: {candidate.gpa}, ID: {candidate.id}, Name: {candidate.name}")

        elif choice == "5":
            min_gpa = float(input("Enter minimum GPA: "))
            required_skills = input("Enter required skills (comma separated): ").split(",")
            min_experience = int(input("Enter minimum experience (in years): "))
            min_coding_marks = float(input("Enter minimum coding test marks: "))
            shortlisted = system.shortlist_candidates(min_gpa, required_skills, min_experience, min_coding_marks)
            if shortlisted:
                print(f"*Shortlisted candidates with min GPA {min_gpa}, skills {required_skills}, "
                      f"min experience {min_experience}, and min coding test marks {min_coding_marks}*:")
                for candidate in shortlisted:
                    print(f"ID: {candidate.id}, Name: {candidate.name}, GPA: {candidate.gpa}, "
                          f"Experience: {candidate.experience}, Skills: {', '.join(candidate.skills)}, "
                          f"Coding Marks: {candidate.coding_marks}")
            else:
                print("No candidates matched the criteria.")

        elif choice == "6":
            min_marks = float(input("Enter minimum marks in coding test: "))
            filtered = system.filter_candidates_by_coding_marks(min_marks)
            if filtered:
                print(f"Candidates with coding test marks >= {min_marks}:")
                for candidate in filtered:
                    print(f"ID: {candidate.id}, Name: {candidate.name}, GPA: {candidate.gpa}, "
                          f"Experience: {candidate.experience}, Skills: {', '.join(candidate.skills)}, "
                          f"Coding Marks: {candidate.coding_marks}")
            else:
                print("No candidates found with the specified coding test marks.")

        elif choice == "7":
            time = input("Enter interview time (e.g., '10:00 AM'): ")
            id = int(input("Enter candidate ID: "))
            system.scheduler.add_slot(time)
            candidate = system.search_candidate_by_id(id)
            if candidate:
                if system.scheduler.schedule_candidate(time, candidate):
                    print(f"Candidate {candidate.name} scheduled for interview at {time}.")
                else:
                    print("Slot already taken or not available.")
            else:
                print("Candidate not found.")

        elif choice == "8":
            schedule = system.scheduler.get_schedule()
            print("Interview Schedule:")
            for time, candidate_name in schedule:
                print(f"Time: {time}, Candidate: {candidate_name}")

        elif choice == "9":
            report = system.generate_report()
            print("\nReport:")
            print(f"Total candidates: {report['total_candidates']}")
            print(f"Shortlisted candidates: {report['shortlisted_candidates']}")
            print("Details of all candidates:")
            for candidate in report['all_candidates']:
                print(f"ID: {candidate[0]}, Name: {candidate[1]}, GPA: {candidate[2]}, "
                      f"Experience: {candidate[3]}, Skills: {candidate[4]}, Coding Marks: {candidate[5]}")
                
        elif choice == "10":
            id = int(input("Enter candidate ID to delete: "))
            system.delete_candidate(id)  

        elif choice == "11":
            print("Exiting the system.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()