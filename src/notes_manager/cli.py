import os
import logging
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel

from logger import setup_logging
from models import Note, NotesStorage


class Mode(Enum):
    ALL_NOTES = "all_notes"
    BY_TAG = "by_tag"
    DELETE = "delete"
    NOTE_CREATED = "note_created"
    CONTINUE = "continue"
    BREAK = "break"


def clear_screen() -> None:
    """Очищает терминал от предыдущего вывода."""
    os.system('cls' if os.name == 'nt' else 'clear')


def create_menu_panel() -> Panel:
    """Для отображения возможных действий"""
    return Panel(
        "[bold]1.[/bold] Добавить заметку\n"
        "[bold]2.[/bold] Показать все заметки\n"
        "[bold]3.[/bold] Найти по тегу\n"
        "[bold]4.[/bold] Удалить заметку\n"
        "[bold]5.[/bold] Выход",
        title="Меню",
        border_style="cyan"
    )


def show_dialog(console: Console, notes_storage: NotesStorage) -> Mode | tuple[Mode, int, bool]:
    """Для обработки ввода пользователя"""
    console.rule(style="cyan")
    action = Prompt.ask("Выберите действие: ", choices=["1", "2", "3", "4", "5"])
    match action:
        case "1":
            return create_note(console, notes_storage)
        case "2":
            return Mode.ALL_NOTES
        case "3":
            return Mode.BY_TAG
        case "4":
            note_id = IntPrompt.ask("Введите ID удаляемой заметки")
            if Confirm.ask("Вы уверены, что хотите удалить эту заметку?", default=True):
                return Mode.DELETE, note_id, notes_storage.delete_note(note_id)
            else:
                return Mode.CONTINUE
        case _:
            console.print("[bold red]Завершение работы[/bold red]")
            return Mode.BREAK


def create_note(console: Console, notes_storage: NotesStorage) -> Mode:
    """Для создания новой заметки"""
    clear_screen()
    console.rule("[bold green]Создать заметку?[/bold green]", style="green", align="left")
    panel = Panel(
        "[bold]1.[/bold] Продолжить создание заметки\n"
        "[bold]2.[/bold] Отмена",
        title="Подтверждение действия",
        border_style="green"
    )
    console.print(panel)
    console.rule(style="green")
    action = Prompt.ask("Выберите действие", choices=["1", "2"])
    match action:
        case "1":
            console.print("\nПоля, помеченные [bold red]*[/bold red] - обязательны для заполнения.\n")
            text = Prompt.ask("[bold red]*[/bold red] Введите текст заметки")
            tags = []
            tags.append(Prompt.ask("[bold red]*[/bold red] Выберите теги приоритета", choices=["важно", "неважно"]))
            tags.append(Prompt.ask("[bold red]*[/bold red] Выберите теги приоритета", choices=["срочно", "несрочно"]))
            tags += [tag.strip() for tag in Prompt.ask("Введите дополнительные теги, через запятую", default="прочее").split(",")]
            notes_storage.add_note(text, tags)
            return Mode.NOTE_CREATED
        case _:
            return Mode.CONTINUE



def show_list_notes(notes: list[Note],
                    tag: str = "",
                    color: str = "magenta") -> Table | None:
    """Для отображения заметок (всех существующих, или по тегу)"""
    
    if tag:
        title = f'Найденные заметки по тегу "{tag}"'
    else:
        title = "Сохраненные заметки"

    table = Table(title=f"\n[bold {color}]{title}[/bold {color}]", show_lines=True, style=color)
    table.add_column("ID")
    table.add_column("Текст заметки")
    table.add_column("Теги")
    table.add_column("Время создания")
    
    for note in notes:
        tag_color = get_priority_color(note)
        tail_tags = [f"[dodger_blue3]{tag}[/dodger_blue3]" for tag in note.tags[2:]] 
        colored_tags = [f"[bold {tag_color}]{tag}[/bold {tag_color}]" for tag in note.tags[:2]] + tail_tags
        table.add_row(str(note.id), f"[{tag_color}]{note.text}[/{tag_color}]", ", ".join(colored_tags), note.created_at)

    if not notes:
        return None
        
    return table


def get_priority_color(note: Note) -> str:
    """Определяет цвет заметки на основе её приоритетных тегов."""
    tags = note.tags
    match tags[:2]:
        case ["важно", "срочно"]:
            return "red"
        case ["важно", "несрочно"]:
            return "dark_orange"
        case ["неважно", "срочно"]:
            return "yellow"
        case ["неважно", "несрочно"]:
            return "green"
        case _:
            return "grey100"


def main() -> None:
    """Точка входа приложения. Запускает главный цикл меню."""
    setup_logging()
    logger = logging.getLogger(__name__)
    console = Console()
    notes_storage = NotesStorage()


    mode = None
    tag = ""
    note_id = 0
    deleted = False
    while True:
        clear_screen()
        if mode == Mode.ALL_NOTES:
            console.rule("[bold magenta]ДАННЫЕ ЗАГРУЖЕНЫ[/bold magenta]", style="magenta")
            console.print(show_list_notes(notes_storage.get_all_notes()))
            console.rule(style="magenta")
        elif mode == Mode.BY_TAG:
            data = show_list_notes(notes_storage.find_by_tag(tag), tag)
            clear_screen()
            if data:
                console.rule("[bold magenta]ДАННЫЕ ЗАГРУЖЕНЫ[/bold magenta]", style="magenta")
                console.print(data)
                console.rule(style="magenta")
                logger.info(f"Поиск по тегу: {tag}")
                console.rule(style="magenta")
            else:
                console.rule("[bold red]ЗАМЕТКИ НЕ НАЙДЕНЫ[/bold red]", style="red")
                console.print(f'[bold italic red]Заметок по тегу "{tag}" не найдено[/bold italic red]')
                console.rule(style="red")
                logger.info(f"Поиск по тегу: {tag}")
                console.rule(style="red")

        elif mode == Mode.DELETE:
            if deleted:
                console.rule("[bold red]ЗАМЕТКИ ПОСЛЕ УДАЛЕНИЯ[/bold red]", style="red")
                console.print(show_list_notes(notes_storage.get_all_notes(), tag, "red"))
                console.rule(style="red")
                console.print("\n[red]Заметка удалена![/red]")
                logger.info(f"Удалена заметка #{note_id}")
                console.rule(style="red")
                Prompt.ask("\nДля возврата в главное меню нажмите `Enter`")
                mode = None
                continue
            else:
                console.rule(style="red")
                logger.warning(f"Попытка удалить несуществующую заметку #{note_id}")
                console.rule(style="red")
                

        console.rule(style="cyan")
        console.print(create_menu_panel())

        dialog = show_dialog(console, notes_storage)
        if dialog == Mode.CONTINUE:
            mode = None
            continue
        elif dialog == Mode.NOTE_CREATED:
            clear_screen()
            console.rule(style="green")
            logger.info(f"Создана заметка {notes_storage.get_all_notes()[-1]}")
            console.rule(style="green")
            mode = None
            Prompt.ask("Для возврата в главное меню нажмите `Enter`")
        elif dialog == Mode.BREAK:
            break
        elif dialog == Mode.ALL_NOTES:
            mode = Mode.ALL_NOTES
            tag = ""
        elif dialog == Mode.BY_TAG:
            mode = Mode.BY_TAG
            tag = Prompt.ask("Введите тег для поиска заметок")
        elif isinstance(dialog, tuple) and dialog[0] == Mode.DELETE:
            mode = Mode.DELETE
            note_id = dialog[1]
            deleted =  dialog[2]


if __name__ == "__main__":
    main()
