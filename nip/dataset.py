from __future__ import annotations
import os, re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union
from copy import copy
from .helper import *
from .error import *


# dataclasses
@dataclass
class DataItem:
    """
    Contains structured data information.
    
    Attributes:
        by_depth (Dict[int, Dict[str, List[str]]]): A dictionary with depth as the key and a dictionary of session path and file names as the value.
    """
    by_depth: Dict[int, Dict[str, List[str]]]


@dataclass
class FileItem:
    """
    Contains information related to a file.

    Attributes:
        subject (str): The subject associated with the file.
        session (Optional[str]): The session associated with the file. Can be None.
        modal (Optional[str]): The modal associated with the file. Can be None.
        annotation (Optional[str]): The annotation associated with the file. Can be None.
        absdir (str): The absolute directory where the file is located.
        filename (str): The name of the file.
        fileext (str): The extension of the file.

    Methods:
        abspath: Return the absolute path of the file.
        basename: Return the base name of the file.
        modify: Modify the name of the file.
        match: Check if the filename matches a regular expression.
        is_match: Check if the filename matches a regular expression.
        has_ext: Check if the file has a specific extension.
    """
    subject: str
    session: Optional[str]
    modal: Optional[str]
    annotation: Optional[str]
    absdir: str
    filename: str
    fileext: str

    @property
    def abspath(self) -> str:
        return os.path.join(self.absdir, self.basename)

    @property
    def basename(self) -> str:
        return f"{self.filename}.{self.fileext}"

    def modify(
        self, 
        replace: Optional[Replace] = None,
        prefix: Optional[str] = None, 
        suffix: Optional[str] = None,
        ext: Optional[str] = None,
        absdir: Union[bool, str] = False
        ) -> str:
        
        if all([e == None for e in [prefix, suffix, replace, ext]]):
            if absdir:
                if isinstance(absdir, bool):
                    return self.abspath
                else:
                    return os.path.join(absdir, self.basename)
            else:
                return self.basename
        else:
            modified = str(self.filename)
            if replace:
                compiled = re.compile(replace.regex)
                modified = compiled.sub(replace.replacement, modified)
            if prefix:
                modified = f"{prefix}{modified}"
            if suffix:
                modified = f"{modified}{suffix}"
            if ext:
                ext = ".".join(strip_empty_str_in_list(ext.split(".")))
            else:
                ext = self.fileext
            
            modified = f"{modified}.{ext}"
            if absdir:
                if isinstance(absdir, bool):
                    return os.path.join(self.absdir, modified)
                else:
                    return os.path.join(absdir, modified)
            else:
                return modified

    def match(self, regex: str) -> Union[dict, Tuple[str], None]:
        groups = re.compile(regex)
        matched = groups.match(self.filename)
        if matched:
            if groups.groupindex:
                return matched.groupdict()
            else:
                return matched.groups()
        else:
            return None
        
    def is_match(self, regex: str) -> bool:
        groups = re.compile(regex)
        matched = groups.match(self.filename)
        if matched:
            return True
        else:
            return False

    def has_ext(self, ext: str) -> bool:
        this_ext = strip_empty_str_in_list(self.fileext.split("."))
        quer_ext = strip_empty_str_in_list(ext.split('.'))
        return this_ext == quer_ext

    def __repr__(self):
        path_list = self.absdir.split(os.sep)
        if self.session == None:
            depth = 3
        else:
            depth = 4
        path = os.sep.join(path_list[-1*depth:])
        
        repr = f"FileItem('{path}', '{self.basename}')"
        return repr
        
    def __str__(self):
        return self.abspath
        

@dataclass
class SessionItem:
    """
    Contains information related to a session.

    Attributes:
        subject (str): The subject associated with the session.
        session (Optional[str]): The specific session. Can be None.
        files (Union[List[FileInfo], Dict[str, List[FileInfo]]]): The files associated with the session. Can be a list or a dictionary.

    Methods:
        length: Return the number of files in the session.
    """
    subject: str
    session: Optional[str]
    files: Union[List[FileItem], Dict[str, List[FileItem]]]

    @property
    def length(self) -> Union[int, Dict[str, int]]:
        if isinstance(self.files, dict):
            return {modal:len(finfos) for modal, finfos in self.files.items()}
        else:
            return len(self.files)
        
    def __repr__(self):
        if isinstance(self.length, dict):
            files = ", ".join([f"{modal}:[n={length}]" for modal, length in self.length.items()])
            files = f'{{{files}}}'
        else:
            files = f"n={self.length}"
        contents = [self.subject, files]
        if self.session != None:
            contents.insert(1, self.session)
        contents = ", ".join(contents)
        return f"SessionItem({contents})"


@dataclass
class StepItem:
    """
    Contains information related to a step in a pipeline.

    Attributes:
        id (str): The id of the step.
        name (str): The name of the step.
        annotation (str): The annotation of the step.
        dataset (Optional[StepDataset]): The dataset associated with the step. Can be None.

    Methods:
        path: Return the path of the step.
    """
    id: str
    name: str
    annotation: str
    dataset: Optional[StepDataset]

    @property
    def path(self) -> str:
        return f"{self.id}_{self.name}_{self.annotation}"
    
    
@dataclass
class MaskItem:
    """
    Contains information related to a mask.

    Attributes:
        modal (str): The modality of the mask.
        dataset (Optional[StepDataset]): The dataset associated with the mask. Can be None.
    """
    modal: str
    dataset: Optional[StepDataset]


@dataclass
class Inherits:
    """
    Contains information to be inherited by a new instance of a class.

    Attributes:
        subjects (List[str]): A list of subjects.
        sessions (List[str]): A list of sessions.
        modal (Optional[List[str]]): A list of modalities. Can be None.
        file_list (List[FileInfo]): A list of FileInfo objects.
        session_list (List[SessionInfo]): A list of SessionInfo objects.
    """
    subjects: List[str]
    sessions: List[str]
    modal: Optional[List[str]]
    file_list: List[FileItem]
    session_list: List[SessionItem]
    

@dataclass
class Replace:
    """
    Contains information related to a replacement operation.

    Attributes:
        regex (str): The regular expression to be matched.
        replacement (str): The string that will replace the matched expression.
    """
    regex: str
    replacement: str


@dataclass
class MaxDepthRef:
    """
    Contains reference values for maximum depth.

    Attributes:
        single_session (int): The reference value for a single session.
        multi_session (int): The reference value for a multi-session.

    Methods:
        list: Returns a list containing the single_session and multi_session values.
    """
    single_session: int
    multi_session: int
    
    @property
    def list(self):
        return [self.single_session, self.multi_session]


# dataset classes
class BaseParser:
    """
    This class is designed to parse files and directories at a given path. It enables the processing of neuroimaging datasets in
    a structured and flexible manner.

    It can be used as a standalone parser or as a base class for more specific parsers. It provides support for parsing both files
    and directories, depth tracking, flexible filtering, and BIDS validation. The parser also implements .nipignore for better
    control over the parsing process.
    
    Public Attributes:
    - dir_only (bool): If True, only directories will be parsed.
    - max_depth (int): The maximum depth of the directory tree.
    - subjects (Optional[List[str]]): List of subjects found in the dataset.
    - sessions (Optional[List[str]]): List of sessions found in the dataset.
    - modals (Optional[List[str]]): List of modalities found in the dataset.
    - file_list (Optional[List[FileInfo]]): List of files parsed in the dataset.
    - session_list (Optional[List[SessionInfo]]): List of sessions found in the dataset.
    
    Private Attributes:
    - _abs_path (str): The absolute path of the root.
    - _abs_path_list (List[str]): The list representation of the absolute path.
    - _abs_path_depth (int): The total depth of the root path.
    - _files_by_depth (DataInfo): A dictionary mapping from depth to another dictionary, which maps from relative 
                                  paths to filenames.
    - _dirs_by_depth (DataInfo): A dictionary mapping from depth to another dictionary, which maps from relative 
                                 paths to directory names.
    """
    
    # public properties
    dir_only: bool
    max_depth: int
    subjects: Optional[List[str]]
    sessions: Optional[List[str]]
    modals: Optional[List[str]]
    file_list = Optional[List[FileItem]]
    session_list = Optional[List[SessionItem]]
    
    # private properties
    _abs_path: str
    _abs_path_list: List[str]
    _abs_path_depth: int
    _files_by_depth: DataItem
    _dirs_by_depth: DataItem

    """
    This class is used to parse files and dirs at a specific path.

    TODO: implement .nipignore for the project
    """
    def __init__(self, path: str, dir_only: bool = False):
        """
        Initialize the BaseParser instance.
        
        Parameters:
        - path (str): The root path of the dataset to parse. Default is None.
        - dir_only (bool): If True, only directories will be parsed. Default is False.
        """
        self.path = path
        self.dir_only = dir_only
        self.parse()
    
    def parse(self):
        self._init_process()
        self._parse_all()

    def _init_process(self):
        """
        Initialize the process by setting up private-level attributes for the root path.

        Attributes:
        - _abs_path (str): The absolute path of the root.
        - _abs_path_list (list): The list representation of the absolute path.
        - _abs_path_depth (int): The total depth of the root path.
        """
        abs_path = os.path.abspath(self.path)
        abs_path_list = strip_empty_str_in_list(abs_path.split(os.path.sep))
        abs_path_depth = len(abs_path_list)
        
        #store to class's private attributes
        self._abs_path = abs_path
        self._abs_path_list = abs_path_list
        self._abs_path_depth = abs_path_depth
        
    def _parse_all(self):
        """
        Parse all subdirectories and files, store them in private attributes, and measure the maximum depth.

        Private Attributes:
        - _files_by_depth (dict): A dictionary mapping from depth to another dictionary, which maps from relative 
                                  paths to filenames.
        - _dirs_by_depth (dict): A dictionary mapping from depth to another dictionary, which maps from relative 
                                 paths to directory names.

        Public Attributes:
        - max_depth (int): The maximum depth of the directory tree.
        """
        max_depth = 0
        files_by_depth = dict()
        dirs_by_depth = dict()
        for (dirpath, dirnames, filenames) in os.walk(self._abs_path):
            dirpath = str_to_list(dirpath)
            relpath = dirpath[self._abs_path_depth:]
            depth_step = len(relpath)

            if len(dirnames) == 0:
                # update max depth
                if depth_step > max_depth:
                    max_depth = depth_step
            else:
                if depth_step not in dirs_by_depth.keys():
                    dirs_by_depth[depth_step] = dict()
                dirs_by_depth[depth_step][os.path.sep.join(relpath)] = sorted(dirnames)

            if not self.dir_only:
                if len(filenames):
                    if depth_step not in files_by_depth.keys():
                        files_by_depth[depth_step] = dict()    
                    files_by_depth[depth_step][os.path.sep.join(relpath)] = sorted(filenames)

        self._files_by_depth = files_by_depth
        self._dirs_by_depth = dirs_by_depth
        self.max_depth = max_depth
    
    @classmethod
    def _validator(cls, 
                   dirs: DataItem, 
                   files: DataItem, 
                   max_depth: int, 
                   ref: MaxDepthRef,
                   modal: bool = False,
                   dir_only: bool = False) -> Tuple[List[str], List[str], List[str]]:
        """
        Validate the dataset structure according to BIDS standards.

        This method verifies the depth of the dataset based on the provided reference for single-session and multi-session datasets, 
        and validates the compliance of the subject, session (optional), modal, and file names with BIDS naming conventions. 
        If any element is not compliant, an UserWarning is issued.

        The validated subjects and sessions are stored in the `subjects` and `sessions` attributes of the instance.

        Raises:
        - ValueError: If the dataset depth is not compliant with BIDS standards.
        - UserWarning: If subject, session, or file names are not compliant with BIDS naming conventions, 
            a warning is issued instead of raising an error.
            
        Returns:
        - A tuple of three lists containing the validated subjects, sessions, and modals.
        """
        # check dataset depth, 2 for single session and 3 for multi session dataset
        if max_depth not in ref.list:
            raise ValueError(f"Invalid dataset depth: {max_depth}. Expected depth is {ref.single_session} "
                             f"for single session or {ref.multi_session} for multi session dataset.")
        
        # define regular expressions for BIDS naming conventions
        subj_pattern = re.compile(r'sub-[a-zA-Z0-9]+')
        sess_pattern = re.compile(r'ses-[a-zA-Z0-9]+')
        file_pattern = re.compile(r'sub-[a-zA-Z0-9]+(_ses-[a-zA-Z0-9]+)?.*')
        
        # validate subject names
        subjects = sorted([s for s in dirs.by_depth[0]['']])
        is_subjects = [subj_pattern.match(s) != None for s in subjects]
        if not all(is_subjects):
            for i, subj in enumerate(subjects):
                # If a subject name does not match the required pattern, warn about a potential compliance issue
                if is_subjects[i]:
                    warn(f"The folder '{subj}' is excluded because it does not match the expected 'sub-*' format.", UserWarning)
                subjects = [s for i, s in enumerate(subjects) if is_subjects[i]]
        
        # if multi session dataset, validate session names
        if max_depth == ref.multi_session:
            sessions = sorted(list(set([sess for sesses in dirs.by_depth[ref.multi_session].values() for sess in sesses])))
            is_sessions = [sess_pattern.match(s) != None for s in sessions]
            if not all(is_sessions):
                for i, sess in enumerate(sessions):
                    # If a session name does not match the required pattern, warn about a potential compliance issue
                    if is_sessions[i]:
                        warn(f"The folder '{sess}' is excluded because it does not match the expected 'ses-*' format.", UserWarning)
                    sessions = [s for i, s in enumerate(sessions) if is_sessions[i]]
        else:
            sessions = None

        # if files are included in parsing, validate file names
        if not dir_only:
            filenames = sorted([filename for sess in files.by_depth[max_depth].values() for filename in sess])
            is_not_bidsfiles = [filename for filename in filenames if file_pattern.match(filename) == None]
            if len(is_not_bidsfiles):
                for relpath, sess in files.by_depth[max_depth].items():
                    for filename in sess:
                        filepath = os.path.join(relpath, filename)
                        warn(f"'{filepath}' does not match the expected BIDS file format.", UserWarning)
        
        # returns validated subjects and sessions
        if modal:
            modals = sorted(list(set([modal for modals in dirs.by_depth[max_depth-1].values() for modal in modals])))
        else:
            modals = None
        return subjects, sessions, modals
        
    def _inherits(self, inherits: Inherits):
        """
        A dataclass to carry over attributes when generating a new instance of a class.

        This class is designed to store the required information when generating a new instance
        with filtered file_list and session_list.

        Attributes:
        - subjects (List[str]): A list of subjects in the dataset.
        - sessions (List[str]): A list of sessions in the dataset.
        - modal (Optional[List[str]]): An optional list of modalities in the dataset. This could be None.
        - file_list (List[FileInfo]): A list of FileInfo objects representing the files in the dataset.
        - session_list (List[SessionInfo]): A list of SessionInfo objects representing the sessions in the dataset.
        """
        self.sessions = inherits.sessions
        self.subjects = inherits.subjects
        self.modals = inherits.modal
        self.file_list = inherits.file_list
        self.session_list = inherits.session_list
    
    def _constructor(self,
                     files: DataItem,
                     ref: MaxDepthRef,
                     modal: bool = False) -> Tuple[List[SessionItem], List[FileItem]]:
        """
        Process the data and construct session and file lists.

        Parameters:
        - files (DataInfo): Data containing the file paths.
        - ref (MaxDepthRef): Reference to the maximum depth.
        - modal (bool): If True, the modal attribute will be considered. Default is False.

        Returns:
        - Tuple: A tuple containing a list of SessionInfo objects and a list of FileInfo objects.
        """
    
        # prep spaceholders
        processed = []
        session_list = []
        file_list = []
        
        # loop over the paths at max depth
        for sess_path, filenames in files.by_depth[self.max_depth].items():
            
            # parse meta data
            if self.max_depth == ref.single_session:
                if modal:
                    subj, modal = str_to_list(sess_path)
                else:
                    subj = str_to_list(sess_path)[0]
                    modal = None
                sess = None
            elif self.max_depth == ref.multi_session:
                if modal:
                    subj, sess, modal = str_to_list(sess_path)
                else:
                    subj, sess = str_to_list(sess_path)
                    modal = None
            else:
                raise ValueError(f"Invalid dataset depth: {self.max_depth}. Expected depth is {ref.single_session} "
                                 f"for single session or {ref.multi_session} for multi session dataset.")

            # construct session and file lists
            task_id = f"{subj}-{sess}"
            if task_id in processed:
                sinfo = [si for si in session_list if si.subject == subj and si.session == sess][0]
            else:
                if modal:
                    sinfo = SessionItem(subj, sess, {})
                else:
                    sinfo = SessionItem(subj, sess, [])
                session_list.append(sinfo)
                processed.append(task_id)
            for f in filenames:
                filename, fileext = f.split('.', 1)
                finfo = FileItem(subj, sess, modal, self._abs_path_list[-1], 
                                 os.path.join(self._abs_path, sess_path), filename, fileext)
                if modal:
                    if modal not in sinfo.files.keys():
                        sinfo.files[modal] = []
                    sinfo.files[modal].append(finfo)
                    file_list.append(finfo)
                else:
                    sinfo.files.append(finfo)
                    file_list.append(finfo)
            
            if modal:
                sinfo.files[modal] = sorted(sinfo.files[modal], key=lambda x: (x.filename, x.fileext))
            else:        
                sinfo.files = sorted(sinfo.files, key=lambda x: (x.modal, x.filename, x.fileext))
        
        # sort constructed lists and returns
        session_list = sorted(session_list, key=lambda x: (x.subject, x.session))
        file_list = sorted(file_list, key=lambda x: (x.subject, x.session, x.modal, x.filename, x.fileext))
        return session_list, file_list

    @classmethod
    def _filter(cls,
                file_list: List[FileItem],
                session_list: List[SessionItem],
                subject: Union[List[str], str, None] = None, 
                session: Union[List[str], str, None] = None,
                modal: Union[List[str], str, None] = None,
                annotation: Union[List[str], str, None] = None,
                regex: Optional[str] = None,
                regex_ignore: Optional[str] = None,
                ext: Optional[str] = None):
        """
        Filter the file list and session list based on the specified criteria.

        Parameters:
        - file_list (List[FileInfo]): List of FileInfo objects to filter.
        - session_list (List[SessionInfo]): List of SessionInfo objects to filter.
        - subject (Union[List[str], str, None]): Subject(s) to filter by. Default is None.
        - session (Union[List[str], str, None]): Session(s) to filter by. Default is None.
        - modal (Union[List[str], str, None]): Modal(s) to filter by. Default is None.
        - annotation (Union[List[str], str, None]): Annotation(s) to filter by. Default is None.
        - regex (Optional[str]): Regex pattern to filter by. Default is None.
        - regex_ignore (Optional[str]): Regex pattern to ignore. Default is None.
        - ext (Optional[str]): File extension to filter by. Default is None.

        Returns:
        - filtered_file_list, filtered_sess_list: Filtered lists of FileInfo and SessionInfo objects.
        """
        filtered_file_list = copy(file_list)
        filtered_sess_list = copy(session_list)
        if subject:
            if isinstance(subject, str):
                subject = [subject]
            filtered_file_list = [finfo for finfo in filtered_file_list if finfo.subject in subject]
            filtered_sess_list = [sinfo for sinfo in filtered_sess_list if sinfo.subject in subject]
        if session:
            if isinstance(session, str):
                session = [session]
            filtered_file_list = [finfo for finfo in filtered_file_list if finfo.session in session]
            filtered_sess_list = [sinfo for sinfo in filtered_sess_list if sinfo.session in session]
        if modal:
            if isinstance(modal, str):
                modal = [modal]
            filtered_file_list = [finfo for finfo in filtered_file_list if finfo.modal in modal]
        if annotation:
            if isinstance(annotation, str):
                annotation = [annotation]
            filtered_file_list = [finfo for finfo in filtered_file_list if finfo.annotation in annotation]
        if ext:
            filtered_file_list = [finfo for finfo in filtered_file_list if finfo.has_ext(ext)]
        if regex:
            filtered_file_list = [finfo for finfo in filtered_file_list if finfo.is_match(regex)]
        if regex_ignore:
            filtered_file_list = [finfo for finfo in filtered_file_list if not finfo.is_match(regex_ignore)]
        
        filtered_sess_list = cls._session_filter(filtered_sess_list,
                                                 modal,
                                                 annotation,
                                                 regex,
                                                 regex_ignore,
                                                 ext)
        
        return filtered_file_list, filtered_sess_list
    
    @classmethod
    def _session_filter(cls, 
                        session_list: List[SessionItem],
                        modal: Union[List[str], str, None] = None,
                        annotation: Union[List[str], str, None] = None,
                        regex: Optional[str] = None, 
                        regex_ignore: Optional[str] = None, 
                        ext: Optional[str] = None):
        """
        Filter the session list based on the specified criteria.

        Parameters:
        - session_list (List[SessionInfo]): List of SessionInfo objects to filter.
        - modal (Union[List[str], str, None]): Modal(s) to filter by. Default is None.
        - annotation (Union[List[str], str, None]): Annotation(s) to filter by. Default is None.
        - regex (Optional[str]): Regex pattern to filter by. Default is None.
        - regex_ignore (Optional[str]): Regex pattern to ignore. Default is None.

        Returns:
        - filtered_sess_list: Filtered list of SessionInfo objects.
        """
        session_list = [copy(s) for s in session_list]
        for sess in session_list:   
            if modal:
                if isinstance(modal, str):
                    modal = [modal]
                if isinstance(sess.files, dict):
                    sess.files = {m:[f for f in fs if f.modal in modal] for m, fs in sess.files.items()}
                else:
                    sess.files = [finfo for finfo in sess.files if finfo.modal in modal]
            if annotation:
                if isinstance(annotation, str):
                    annotation = [annotation]
                if isinstance(sess.files, dict):
                    sess.files = {m:[f for f in fs if f.annotation in annotation] for m, fs in sess.files.items()}
                else:
                    sess.files = [finfo for finfo in sess.files if finfo.annotation in annotation]
            if regex:
                if isinstance(sess.files, dict):
                    sess.files = {m:[f for f in fs if f.is_match(regex)] for m, fs in sess.files.items()}
                else:
                    sess.files = [finfo for finfo in sess.files if finfo.is_match(regex)]
            if regex_ignore:
                if isinstance(sess.files, dict):
                    sess.files = {m:[f for f in fs if not f.is_match(regex_ignore)] for m, fs in sess.files.items()}
                else:
                    sess.files = [finfo for finfo in sess.files if not finfo.is_match(regex_ignore)]
            if ext:
                if isinstance(sess.files, dict):
                    sess.files = {m:[f for f in fs if f.has_ext(ext)] for m, fs in sess.files.items()}
                else:
                    sess.files = [finfo for finfo in sess.files if finfo.has_ext(ext)]
            if isinstance(sess.files, dict):
                sess.files = {k:v for k, v in sess.files.items() if len(v)}
            
        return session_list


class RawDataset(BaseParser):
    """
    Class for handling and parsing NIP-RawDataset specifications which correspond to BIDS standards.

    Attributes:
        path (str): The root path of the dataset to parse.
        inherits (Optional[Inherits]): Optional Inherits object with information to be inherited by a new instance of a class.

    Methods:
        __init__: Initialize the RawDataset instance.
        _validate: Validate the dataset structure according to BIDS standards.
        _construct: Construct session_list and file_list.
        filter: Filter data based on several criteria.
    """
    def __init__(self, 
                 path: str, 
                 validate: bool = True,
                 inherits: Optional[Inherits] = None,
                 *args, **kwargs):
        """
        Initialize the StepDataset instance.

        Parameters:
        path (str): The root path of the dataset to parse.
        validate (bool, optional): If True, validation of the dataset structure is performed on initialization. Default is True.
        inherits (Inherits, optional): Optional Inherits object with information to be inherited by a new instance of a class.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(path, *args, **kwargs)
        if validate:
            self._validate()
        if inherits:
            self._inherits(inherits)
        else:
            self._construct()

    def _validate(self):
        """
        Validate the dataset structure according to the provided reference and modality.
        """
        dirs = DataItem(self._dirs_by_depth)
        files = DataItem(self._files_by_depth)
        ref = MaxDepthRef(2, 3)
        self.sessions, self.subjects, self.modals = \
            self._validator(dirs, files, self.max_depth, ref, modal=True)

    def _construct(self):
        """
        Construct session_list and file_list from the dataset.
        """
        files = DataItem(self._files_by_depth)
        ref = MaxDepthRef(2, 3)
        modal = True
        
        self.session_list, self.file_list = self._constructor(files, 
                                                              ref, 
                                                              modal)
        
    def filter(self, 
               subject: Union[List[str], str, None] = None, 
               session: Union[List[str], str, None] = None,
               modal: Union[List[str], str, None] = None,
               annotation: Union[List[str], str, None] = None,
               regex: Optional[str] = None,
               regex_ignore: Optional[str] = None,
               ext: Optional[str] = None) -> RawDataset:
        """
        Filter the dataset based on various parameters such as subject, session, modality, annotation, regex, regex_ignore, and extension.

        Parameters:
        subject (Union[List[str], str, None], optional): The subject(s) to filter by.
        session (Union[List[str], str, None], optional): The session(s) to filter by.
        modal (Union[List[str], str, None], optional): The modality(ies) to filter by.
        annotation (Union[List[str], str, None], optional): The annotation(s) to filter by.
        regex (Optional[str], optional): A regex pattern to filter by.
        regex_ignore (Optional[str], optional): A regex pattern to ignore while filtering.
        ext (Optional[str], optional): The file extension to filter by.

        Returns:
        RawDataset: A new instance of StepDataset with filtered data.
        """
        file_list, sess_list = self._filter(self.file_list, 
                                            self.session_list,
                                            subject,
                                            session,
                                            modal,
                                            annotation,
                                            regex,
                                            regex_ignore,
                                            ext)
        
        inherits = Inherits(self.subjects, self.sessions, self.modals,
                            file_list, sess_list)
        return RawDataset(self.path, False, inherits)
            

class StepDataset(BaseParser):
    """
    Class for handling and parsing NIP-ProcDataset specifications. These specifications consist of process 
    step folders containing BIDS-like datasets which do not contain modality subdirectories (only subjects or 
    subjects-sessions).

    Attributes:
        path (str): The root path of the dataset to parse.
        inherits (Optional[Inherits]): Optional Inherits object with information to be inherited by a new instance of a class.

    Methods:
        __init__: Initialize the StepDataset instance.
        _validate: Validate the dataset structure.
        _construct: Construct session_list and file_list.
        filter: Filter data based on several criteria.
    """
    def __init__(self, 
                 path: str, 
                 validate: bool = True, 
                 inherits: Optional[Inherits] = None,
                 *args, **kwargs):
        """
        Initialize the StepDataset instance.

        Parameters:
        path (str): The root path of the dataset to parse.
        validate (bool, optional): If True, validation of the dataset structure is performed on initialization. Default is True.
        inherits (Inherits, optional): Optional Inherits object with information to be inherited by a new instance of a class.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(path, *args, **kwargs)
        if validate:
            self._validate()
        if inherits:
            self._inherits(inherits)
        else:
            self._construct()

    def _validate(self):
        """
        Validate the dataset structure according to the provided reference and modality.
        """
        dirs = DataItem(self._dirs_by_depth)
        files = DataItem(self._files_by_depth)
        ref = MaxDepthRef(1, 2)
        self.sessions, self.subjects, self.modals = \
            self._validator(dirs, files, self.max_depth, ref, modal=False)

    def _construct(self):
        """
        Construct session_list and file_list from the dataset.
        """
        files = DataItem(self._files_by_depth)
        ref = MaxDepthRef(1, 2)
        modal = False
        
        self.session_list, self.file_list = self._constructor(files, 
                                                              ref, 
                                                              modal)

    def filter(self, 
               subject: Union[List[str], str, None] = None, 
               session: Union[List[str], str, None] = None,
               modal: Union[List[str], str, None] = None,
               annotation: Union[List[str], str, None] = None,
               regex: Optional[str] = None,
               regex_ignore: Optional[str] = None,
               ext: Optional[str] = None) -> StepDataset:
        """
        Filter the dataset based on various parameters such as subject, session, modality, annotation, regex, regex_ignore, and extension.

        Parameters:
        subject (Union[List[str], str, None], optional): The subject(s) to filter by.
        session (Union[List[str], str, None], optional): The session(s) to filter by.
        modal (Union[List[str], str, None], optional): The modality(ies) to filter by.
        annotation (Union[List[str], str, None], optional): The annotation(s) to filter by.
        regex (Optional[str], optional): A regex pattern to filter by.
        regex_ignore (Optional[str], optional): A regex pattern to ignore while filtering.
        ext (Optional[str], optional): The file extension to filter by.

        Returns:
        StepDataset: A new instance of StepDataset with filtered data.
        """
       
        file_list, sess_list = self._filter(self.file_list, 
                                            self.session_list,
                                            subject,
                                            session,
                                            modal,
                                            annotation,
                                            regex,
                                            regex_ignore,
                                            ext)
        
        inherits = Inherits(self.subjects, self.sessions, self.modals,
                            file_list, sess_list)
        return StepDataset(self.path, False, inherits)


class ProcDataset:
    """
    Class for processing a dataset.

    Attributes:
        path (str): The root path of the dataset to process.
        is_mask (bool): Flag indicating if the dataset is a mask.

    Methods:
        __init__: Initialize the ProcDataset instance.
        _parse: Parse the dataset.
        _subpath: Return a subpath within the dataset.
        _scan_subpath: Scan a subpath and return a StepDataset.
        get_dataset: Return a dataset based on a provided target.
        avail: Return a list of available datasets.
    """
    def __init__(self, path: str, mask: bool = False):
        self.path = path
        self.is_mask = mask
        self._parse()

    def _parse(self):
        if self.is_mask:
            self.mask_list = []
            for modal in os.listdir(self.path):
                if os.path.isdir(self._subpath(modal)):
                    try:
                        self.mask_list.append(MaskItem(modal, dataset=self._scan_subpath(modal)))
                    except:
                        # empty
                        pass
        else:
            self.step_list = []
            step_pattern = re.compile(r"(?P<id>[0-9]{4})_(?P<name>[a-zA-Z0-9\-]+)_(?P<annotation>[a-zA-Z0-9]+)")
            for step in os.listdir(self.path):
                if os.path.isdir(self._subpath(step)):
                    matched = step_pattern.match(step)
                    if matched:
                        si = matched.groupdict()
                        try:
                            self.step_list.append(StepItem(si["id"], si["name"], si["annotation"], dataset=self._scan_subpath(step)))
                        except:
                            # empty
                            pass

    def _subpath(self, path):
        return os.path.join(self.path, path)

    def _scan_subpath(self, path) -> StepDataset:
        return StepDataset(path=os.path.join(self.path, path))

    @property
    def avail(self):
        if self.is_mask:
            return self.mask_list
        else:
            return self.step_list
        
    def __repr__(self):
        if self.is_mask:
            title = "Available mask dataset:\n"
        else:
            title = "Available processing step dataset:\n"
        return title + '\n'.join([str(e) for e in self.avail])