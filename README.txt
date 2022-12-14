List of optional flags:
  -?                 - Displays the usage screen (Отображает экран использования)
  -p                 - Manages persistent shadow copies (Управляет постоянными теневыми копиями)
  -nw                - Manages no-writer shadow copies (Управляет теневыми копиями без записи)
  -nar               - Creates shadow copies with no auto-recovery (Создает теневые копии без автоматического восстановления)
  -tr                - Creates TxF-recovered shadow copies (Создает TxF-восстановленные теневые копии)
  -ad                - Creates differential HW shadow copies (Создает дифференциальные теневые копии HW)
  -ap                - Creates plex HW shadow copies (Создает теневые копии plex HW)
  -scsf              - Creates Shadow Copies for Shared Folders (Client Accessible) (Создает теневые копии для общих папок (Доступны клиенту))
  -t={file.xml}      - Transportable shadow set. Generates also the backup components doc. (Переносной набор теней. Генерирует также документ о компонентах резервного копирования.)
  -bc={file.xml}     - Generates the backup components doc for non-transportable shadow set. (Генерирует документ о компонентах резервного копирования для нетранспортабельного теневого набора.)
  -wi={Writer Name}  - Verify that a writer/component is included (Убедитесь, что включен писатель/компонент)
  -wx={Writer Name}  - Exclude a writer/component from set creation or restore (Исключить запись/компонент из набора для создания или восстановления)
  -mask              - BreakSnapshotSetEx flag: Mask shadow copy luns from system on break. (флаг BreakSnapshotSetEx: Маска теневого копирования luns из системы при разрыве.)
  -rw                - BreakSnapshotSetEx flag: Make shadow copy luns read-write on break. (BreakSnapshotSetEx флаг: Сделать теневую копию для чтения-записи при разрыве.)
  -forcerevert       - BreakSnapshotSetEx flag: Complete operation only if all disk signatures revertable. (флаг BreakSnapshotSetEx: Завершите операцию, только если все подписи диска можно вернуть.)
  -norevert          - BreakSnapshotSetEx flag: Do not revert disk signatures. (флаг BreakSnapshotSetEx: Не отменять подписи диска.)
  -revertsig         - Revert to the original disk's signature during resync. (Возврат к подписи исходного диска во время повторной синхронизации.)
  -novolcheck        - Ignore volume check during resync. Unselected volumes will be overwritten. (Игнорировать проверку громкости во время повторной синхронизации. Невыбранные тома будут перезаписаны.)
  -script={file.cmd} - SETVAR script creation (Создание сценария SETVAR) 
  -exec={command}    - Custom command executed after shadow creation, import or between break and make-it-write (Пользовательская команда, выполняемая после создания тени, импорта или между break и make-it-write)
  -wait              - Wait before program termination or between shadow set break and make-it-write (Ожидание перед завершением программы или между прерыванием набора теней и записью make-it)
  -tracing           - Runs VSHADOW.EXE with enhanced diagnostics (Запуски VSHADOW.EXE с улучшенной диагностикой)

List of commands:
  {volume list}                   - Creates a shadow set on these volumes (Создает набор теней для этих томов)
  -ws                             - List writer status (Статус записи списка)
  -wm                             - List writer summary metadata (сводные метаданные)
  -wm2                            - List writer detailed metadata (Подробные метаданные для записи списка)
  -wm3                            - List writer detailed metadata in raw XML format (List writer подробные метаданные в формате raw XML)
  -q                              - List all shadow copies in the system (Перечислите все теневые копии в системе)
  -qx={SnapSetID}                 - List all shadow copies in this set (Перечислите все теневые копии в этом наборе)
  -s={SnapID}                     - List the shadow copy with the given ID (Перечисляет теневую копию с заданным идентификатором)
  -da                             - Deletes all shadow copies in the system (Удаляет все теневые копии в системе)
  -do={volume}                    - Deletes the oldest shadow of the specified volume (Удаляет самую старую тень указанного тома)
  -dx={SnapSetID}                 - Deletes all shadow copies in this set (Удаляет все теневые копии в этом наборе)
  -ds={SnapID}                    - Deletes this shadow copy (Удаляет эту теневую копию)
  -i={file.xml}                   - Transportable shadow copy import (Переносной импорт теневой копии)
  -b={SnapSetID}                  - Break the given shadow set into read-only volumes (Разбейте данный набор теней на тома, доступные только для чтения)
  -bw={SnapSetID}                 - Break the shadow set into writable volumes (Разбейте набор теней на тома, доступные для записи)
  -bex={SnapSetID}                - Break using BreakSnapshotSetEx and flags, see options for available flags (Разрыв с использованием BreakSnapshotSetEx и флагов, см. Параметры для доступных флагов)
  -el={SnapID},dir                - Expose the shadow copy as a mount point (Выставить теневую копию в качестве точки монтирования)
  -el={SnapID},drive              - Expose the shadow copy as a drive letter (Указать теневую копию как букву диска)
  -er={SnapID},share              - Expose the shadow copy as a network share (Предоставить теневую копию в качестве общего сетевого ресурса)
  -er={SnapID},share,path         - Expose a child directory from the shadow copy as a share (Предоставить дочерний каталог из теневой копии в качестве общего доступа)
  -r={file.xml}                   - Restore based on a previously-generated Backup Components document (Восстановление на основе ранее созданного документа компонентов резервной копии)
  -rs={file.xml}                  - Simulated restore based on a previously-generated Backup Components doc (Имитированное восстановление на основе ранее сгенерированного документа компонентов резервной копии)
  -revert={SnapID}                - Revert a volume to the specified shadow copy (Возврат тома к указанной теневой копии)
  -addresync={SnapID},drive       - Resync the given shadow copy to the specified volume (Повторно синхронизировать данную теневую копию с указанным томом)
  -addresync={SnapID}             - Resync the given shadow copy to it's original volume (Повторно синхронизирует данную теневую копию с исходным томом)
  -resync=bcd.xml                 - Perform Resync using the specified BCD (Выполнить повторную синхронизацию с использованием указанного BCD)

Examples:
 - Non-persistent shadow copy creation on C: and E: (Создание непостоянной теневой копии на C: и E:)
     VSHADOW C: E:
 - Non-persistent shadow copy creation on a CSV named Volume1 (Создание непостоянной теневой копии в файле CSV с именем Volume1)
     VSHADOW C:\ClusterStorage\Volume1
 - Persistent shadow copy creation on C: (with no writers) (Постоянное создание теневой копии на C: (без авторов))
     VSHADOW -p -nw C:
 - Transportable shadow copy creation on X: (Создание переносной теневой копии на X:)
     VSHADOW -t=file1.xml X:
 - Transportable shadow copy import (Переносной импорт теневой копии)
     VSHADOW -i=file1.xml
 - List all shadow copies in the system: (Список всех теневых копий в системе:)
     VSHADOW -q
