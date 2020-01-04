#!/usr/bin/python3
# -*- coding: utf-8 -*
__author__ = "gisly"
import openpyxl
import os


class ExcelParser:
    total_column_num = 0
    columns_parsed = []
    objects_parsed = []

    column_names = []
    column_correspondences = dict()

    SPECIFIC_WORKSHEET_NAMES = []
    LINE_SEPARATOR = '\n'
    COLUMN_SEPARATOR = '\t'

    def __init__(self, column_settings_filename):
        if not os.path.exists(column_settings_filename):
            raise Exception('No such file:' + column_settings_filename)
        with open(column_settings_filename, 'r', encoding='utf-8') as fin:
            for line in fin:
                column_names_pair = line.strip().split('\t')
                column_name_custom = column_names_pair[0]
                column_name_normalized = column_names_pair[1]
                self.column_correspondences[column_name_custom] = column_name_normalized
                self.column_names.append(column_name_normalized)


    def convert_excel_to_csv(self, filename_in, filename_out):
        self.parse_excel(filename_in)
        self.write_to_csv(filename_out)

    def parse_excel(self, filename_in):
        wb = openpyxl.load_workbook(filename=filename_in)
        for index, sheetname in enumerate(wb.sheetnames):
            self.parse_worksheet(wb[sheetname], sheetname, index)

    #override this method to parse some worksheets in a special way
    def parse_worksheet(self, worksheet, sheetname, worksheet_index):
        self.total_column_num = 0
        for row_index, row in enumerate(worksheet.rows):
            if row_index == 0:
                self.process_column_names(row)
            elif self.is_normal_worksheet(sheetname) and worksheet_index == 0:
                is_empty_row = self.process_object_data(worksheet_index, row, row_index, False)
                if is_empty_row:
                    break
            elif self.is_normal_worksheet(sheetname):
                self.process_object_data(worksheet_index, row, row_index, True)
            else:
                self.process_specific_worksheet(sheetname, worksheet_index, row, row_index)

    def is_normal_worksheet(self, sheetname):
        return sheetname not in self.SPECIFIC_WORKSHEET_NAMES

    def process_specific_worksheet(self, sheetname, worksheet_index, row, row_index):
        pass

    def process_column_names(self, row):
        unknown_column_names = []
        column_name_worksheet = []
        for cell in row:
            column_name = cell.value
            if column_name is None:
                continue
            column_name_worksheet.append(column_name)
            self.total_column_num += 1
            column_correspondence = self.column_correspondences.get(column_name)
            if column_correspondence is None:
                unknown_column_names.append(column_name)
        self.columns_parsed.append(column_name_worksheet)

    def process_object_data(self, worksheet_index, row, row_index, is_existing_object = False):
        if is_existing_object:
            if row_index >= len(self.objects_parsed):
                return
            object_parsed = self.objects_parsed[row_index]
        else:
            object_parsed = dict()
        is_empty_row = True
        for column_index, cell in enumerate(row):
            if column_index >= self.total_column_num:
                break
            column_name = self.columns_parsed[worksheet_index][column_index]
            normalized_name = self.column_correspondences.get(column_name)
            normalized_value = self.normalize_value(normalized_name, cell.value)
            if normalized_name:
                object_parsed[normalized_name] = normalized_value
            if cell.value is not None:
                is_empty_row = False
        if not is_existing_object and not is_empty_row:
            self.objects_parsed.append(object_parsed)
        return is_empty_row

    def normalize_value(self, column_name, column_value):
        #TODO
        if column_value is None:
            return ''
        if type(column_value) == int:
            return column_value
        return column_value.strip().replace('\t', ' ')

    def write_to_csv(self, filename_out):
        with open(filename_out, 'w', encoding='utf-8', newline='') as fout:
            fout.write(self.create_csv_headers() + self.LINE_SEPARATOR)
            for object_parsed in self.objects_parsed:
                fout.write(self.create_csv_line(object_parsed) + self.LINE_SEPARATOR)

    def create_csv_headers(self):
        return self.COLUMN_SEPARATOR.join(self.column_names)

    def create_csv_line(self, object_parsed):
        line_csv = ''
        for column_name in self.column_names:
            line_csv += str(object_parsed.get(column_name, '')) + self.COLUMN_SEPARATOR
        return line_csv.strip()

excel_parser = ExcelParser('settings.ini')

excel_parser.convert_excel_to_csv('D://Expeds/Exped2019/Socio/ankety_2019_Tugur.xlsx', 'test.csv')
