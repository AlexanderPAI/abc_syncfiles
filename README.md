# Выбор правильных абстракций

Посмотрев код (`bad_sync.py`), можно увидеть, что происходят три четко различимые вещи (три отдельные обязанности - responsibilities):
1. Опрашивается файловая система с помощью `os.walk` и определяются хеши для серии путей. Этот код похож и в случае исходного каталога, и каталога места назначения
2. Определяется, является ли файл новым, переименнованным или лишним
3. Копируются, перемещаются или удаляются файлы в соответствии с исходным каталогом


## Пример кода явными зависимостями
```python
def sync(source, dest): # 1
    source_hashes = reader(source_root) # 2
    dest_hashes = reader(dest_root)

    for sha, filename in src_hashes.items():
        if sha not in dest_hashes:
            sourcepath = source_root / filename
            destpath = dest_root / filename
            filesystem.copy(destpath, sourcepath) #3
            
        elif dest_hashes[sha] != filename:
            olddestpath = dest_root / dest_hashes[sha]
            newdestpath = dest_root / filename
            filesystem.move(olddestpath, newdestpath)

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            filesystem.delete(dest_root / filename)
```

1. Верхнеуровневая функция выставляет наружу две новые зависимости: `reader` и `filesystem`
2. Вызываем `reader`, чтобы создать словарь с файлами.
3. Вызываем `filesystem`, чтобы применить обнаруженные изменения.

## Тесты с внедрением зависимостей с использованием подделок (не путать с имитацией(mock))
_Псевдокод_
```python
class FakeFileSystem(lst):
    
    def copy(self, src, dest):
        self.append(('COPY', src, dest))
        
    def move(self, src, dest):
        self.append(('MOVE', src, dest))

    def delete(self, dest):
        self.append(('DELETE', src, dest))

        
# тесты
def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source = {"sha": "my-file"}
    dest = {}
    filesystem = FakeFileSystem()

    reader = {"/source": source, "/dest": dest}
    synchronise_dirs(reader.pop, filesystem, "/source", "/dest")
    
    assert filesystem == [('COPY', "/source/my-file", "/dest/my-file")]


def test_when_a_file_has_been_renamed_in_the_source():
    source = {"sha": "renamed-file"}
    dest = {"sha1": "original-file"}
    filesystem = FakeFileSystem()

    reader = {"/source": source, "/dest": dest}
    synchronise_dirs(reader.pop, filesystem, "/source", "/dest")
    assert filesystem == [('MOVE', "/dest/original-file", "/dest/renamed-file")]
```

## Мнение, почему не стоит использовать `mock.patch` в указанном выше случае
Три основные причины
1. Наложение заплаток на используемые зависимости позволять проводить юнит-тестирование кода, но это никак не улучшает дизайн. Использование `mock.patch` не позволит коду работать, например, с флагом `--dry-run` или с FTP-сервером. Для этого нужно будет ввести абстракции.
2. Тесты с использованием имитаций тяготеют к большей связанности с деталями реализации кодовой базы. Это обусловлено тем, что имитационные тесты проверяют взаимодействие между элементами кода: правильные ли аргументы мы использовали при вызове `shutil.copy`. Такая связанность между кодом и тестом, как правило, делает тесты ненадежными.
3. Чрезмерное использование имитаций приводит к сложным тестам, которые не способны объяснять код.

> `monkey patch` (обезьянья заплатка) или утиный патч - в программировании, возможность подмены методов и значений атрибутов классов во время выполнения программы. **Это признак "smells code""**

## Имитации против подделок - классическая школа TDD против Лондонской

Краткое объяснение между имитациями и подделками:
- Имитации (mocks), или подставные объекты, используются для проверки того, **каким образом** что-то используется; у них есть такие методы, как `assert_called_once_with()` (проверяет, действительно ли метод был вызван только один раз). Они связаны с Лондонской школой TDD
- Подделки (fakes) - это рабочие реализации того, что они заменяют. Подделки предназначены для использования только в тестах. Они не будут работать "в реальной жизни"; репозиторий, расположенный InMemory - хороший пример. Но вы можете реализовать их, чтобы делать утверждения о конечном состоянии системы, а не о поведении в процессе, поэтому они связаны с классическим стилем TDD

